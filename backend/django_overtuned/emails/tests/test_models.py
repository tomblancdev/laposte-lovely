import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from django_overtuned.emails.models import Email
from django_overtuned.emails.models import EmailAccount
from django_overtuned.emails.models import EmailAddresses
from django_overtuned.emails.models import EmailFolder
from django_overtuned.emails.models import EmailFolderPersonalization
from django_overtuned.emails.models import EmailPersonalization
from django_overtuned.emails.tests.factories import EmailAccountFactory
from django_overtuned.emails.tests.factories import EmailAddressesFactory
from django_overtuned.emails.tests.factories import EmailFactory
from django_overtuned.emails.tests.factories import EmailFolderFactory
from django_overtuned.emails.tests.factories import EmailFolderPersonalizationFactory
from django_overtuned.emails.tests.factories import EmailPersonalizationFactory
from django_overtuned.users.tests.factories import UserFactory


class TestEmailAddresses:
    """Test suite for EmailAddresses model."""

    def test_str_method(self, email_address: EmailAddresses):
        """Test string representation of EmailAddresses."""
        assert str(email_address) == email_address.address

    def test_address_is_unique(self, db):
        """Test that email addresses must be unique."""
        address = "test@example.com"
        EmailAddressesFactory(address=address)

        # Attempting to create another with the same address should use get_or_create
        email_address2 = EmailAddressesFactory(address=address)
        assert EmailAddresses.objects.filter(address=address).count() == 1
        assert email_address2.address == address

    def test_address_field_is_email(self, email_address: EmailAddresses):
        """Test that address field contains a valid email format."""
        assert "@" in email_address.address

    def test_reverse_relations_emails_from(self, db):
        """Test reverse relation for emails sent from this address."""
        from_address = EmailAddressesFactory()
        email = EmailFactory(from_address=from_address)

        assert email in from_address.emails_from.all()

    def test_reverse_relations_emails_to(self, db):
        """Test reverse relation for emails sent to this address."""
        to_address = EmailAddressesFactory()
        email = EmailFactory()
        email.to_addresses.add(to_address)

        assert email in to_address.emails_to.all()

    def test_reverse_relations_emails_reply_to(self, db):
        """Test reverse relation for emails with this as reply-to address."""
        reply_to_address = EmailAddressesFactory()
        email = EmailFactory(reply_to_address=reply_to_address)

        assert email in reply_to_address.emails_reply_to.all()


class TestEmailAccount:
    """Test suite for EmailAccount model."""

    def test_str_method(self, email_account: EmailAccount):
        """Test string representation of EmailAccount."""
        expected = f"{email_account.name} ({email_account.user})"
        assert str(email_account) == expected

    def test_user_relationship(self, email_account: EmailAccount):
        """Test that EmailAccount has a valid user relationship."""
        assert email_account.user is not None
        assert email_account.user.email

    def test_content_type_set_on_save(self, db):
        """Test that _content_type is automatically set on save."""
        user = UserFactory()
        account = EmailAccount(user=user, name="Test Account")
        account.save()

        assert account._content_type is not None  # noqa: SLF001
        assert account._content_type == ContentType.objects.get_for_model(EmailAccount)  # noqa: SLF001

    def test_connect_raises_not_implemented(self, email_account: EmailAccount):
        """Test that connect method raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            email_account.connect()

        assert "connect to the email server" in str(exc_info.value)

    def test_retrieve_folders_raises_not_implemented(self, email_account: EmailAccount):
        """Test that retrieve_folders method raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            email_account.retrieve_folders()

        assert "retrieve folders" in str(exc_info.value)

    def test_retrieve_emails_raises_not_implemented(self, email_account: EmailAccount):
        """Test that retrieve_emails method raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            email_account.retrieve_emails()

        assert "retrieve emails" in str(exc_info.value)

    def test_one_to_one_relationship_with_user(self, db):
        """Test that EmailAccount has one-to-one relationship with user."""
        user = UserFactory()
        account1 = EmailAccountFactory(user=user)

        # django_get_or_create should return the same account
        account2 = EmailAccountFactory(user=user)

        assert account1.pk == account2.pk


class TestEmailFolder:
    """Test suite for EmailFolder model."""

    def test_str_method(self, email_folder: EmailFolder):
        """Test string representation of EmailFolder."""
        assert str(email_folder) == email_folder.base_name

    def test_account_relationship(self, email_folder: EmailFolder):
        """Test that EmailFolder has a valid account relationship."""
        assert email_folder.account is not None
        assert isinstance(email_folder.account, EmailAccount)

    def test_base_name_is_unique(self, db, email_account):
        """Test that base_name is unique."""
        base_name = "unique_folder_name"
        folder1 = EmailFolderFactory(base_name=base_name, account=email_account)

        # django_get_or_create should return the same folder
        folder2 = EmailFolderFactory(base_name=base_name, account=email_account)

        assert folder1.pk == folder2.pk

    def test_parent_relationship(self, db, email_account):
        """Test parent-child folder relationship."""
        parent_folder = EmailFolderFactory(account=email_account)
        child_folder = EmailFolderFactory(
            account=email_account,
            parent=parent_folder,
            base_name="child_folder",
        )

        assert child_folder.parent == parent_folder
        assert child_folder in parent_folder.subfolders.all()

    def test_nullable_parent(self, email_folder: EmailFolder):
        """Test that parent can be null for root folders."""
        email_folder.parent = None
        email_folder.save()

        assert email_folder.parent is None

    def test_reverse_relation_subfolders(self, db, email_account):
        """Test reverse relation for subfolders."""
        parent = EmailFolderFactory(account=email_account, base_name="parent")
        child1 = EmailFolderFactory(
            account=email_account,
            parent=parent,
            base_name="child1",
        )
        child2 = EmailFolderFactory(
            account=email_account,
            parent=parent,
            base_name="child2",
        )

        assert child1 in parent.subfolders.all()
        assert child2 in parent.subfolders.all()
        assert parent.subfolders.count() == 2  # noqa: PLR2004

    def test_reverse_relation_emails(self, db, email_folder):
        """Test reverse relation for emails in folder."""
        email1 = EmailFactory(folder=email_folder)
        email2 = EmailFactory(folder=email_folder)

        assert email1 in email_folder.emails.all()
        assert email2 in email_folder.emails.all()


class TestEmail:
    """Test suite for Email model."""

    def test_str_method(self, email: Email):
        """Test string representation of Email."""
        expected = f"[{email.message_id}] {email.subject}"
        assert str(email) == expected

    def test_message_id_is_primary_key(self, email: Email):
        """Test that message_id is the primary key."""
        assert email.pk == email.message_id

    def test_message_id_is_unique(self, db):
        """Test that message_id must be unique."""
        message_id = "unique-message-id-123"
        email1 = EmailFactory(message_id=message_id)

        # django_get_or_create should return the same email
        email2 = EmailFactory(message_id=message_id)

        assert email1.pk == email2.pk

    def test_from_address_relationship(self, email: Email):
        """Test from_address relationship."""
        assert email.from_address is not None
        assert isinstance(email.from_address, EmailAddresses)

    def test_to_addresses_relationship(self, email: Email):
        """Test to_addresses many-to-many relationship."""
        assert email.to_addresses.count() > 0
        for address in email.to_addresses.all():
            assert isinstance(address, EmailAddresses)

    def test_reply_to_address_nullable(self, db):
        """Test that reply_to_address can be null."""
        email = EmailFactory(reply_to_address=None)
        assert email.reply_to_address is None

    def test_in_reply_to_relationship(self, db):
        """Test in_reply_to self-referential relationship."""
        original_email = EmailFactory()
        reply_email = EmailFactory(in_reply_to=original_email)

        assert reply_email.in_reply_to == original_email
        assert reply_email in original_email.replies.all()

    def test_in_reply_to_nullable(self, email: Email):
        """Test that in_reply_to can be null."""
        email.in_reply_to = None
        email.save()
        assert email.in_reply_to is None

    def test_date_fields(self, email: Email):
        """Test date_received and date_sent fields."""
        assert email.date_received is not None
        assert email.date_sent is not None
        assert isinstance(email.date_received, type(timezone.now()))
        assert isinstance(email.date_sent, type(timezone.now()))

    def test_body_fields_can_be_blank(self, db):
        """Test that body_text and body_html can be blank."""
        email = EmailFactory(body_text="", body_html="")
        assert email.body_text == ""
        assert email.body_html == ""

    def test_is_read_default_false(self, db):
        """Test that is_read defaults to False."""
        email = EmailFactory()
        # Refresh from db to ensure we get the database default
        email.refresh_from_db()
        assert email.is_read is False

    def test_folder_relationship(self, email: Email):
        """Test folder relationship."""
        assert email.folder is not None
        assert isinstance(email.folder, EmailFolder)

    def test_folder_nullable(self, db):
        """Test that folder can be null."""
        email = EmailFactory(folder=None)
        assert email.folder is None

    def test_priority_nullable(self, db):
        """Test that priority can be null."""
        email = EmailFactory(priority=None)
        assert email.priority is None

    def test_subject_field(self, email: Email):
        """Test subject field."""
        assert email.subject
        assert len(email.subject) <= 255  # noqa: PLR2004

    def test_json_data_field(self, email: Email):
        """Test json_data field."""
        assert email.json_data is not None
        assert isinstance(email.json_data, dict)

    def test_reverse_relation_replies(self, db):
        """Test reverse relation for replies."""
        original = EmailFactory()
        reply1 = EmailFactory(in_reply_to=original)
        reply2 = EmailFactory(in_reply_to=original)

        assert reply1 in original.replies.all()
        assert reply2 in original.replies.all()
        assert original.replies.count() == 2  # noqa: PLR2004

    def test_multiple_to_addresses(self, db):
        """Test adding multiple to_addresses."""
        email = EmailFactory()
        addr1 = EmailAddressesFactory()
        addr2 = EmailAddressesFactory()

        email.to_addresses.add(addr1, addr2)

        assert addr1 in email.to_addresses.all()
        assert addr2 in email.to_addresses.all()
        assert email.to_addresses.count() >= 2  # noqa: PLR2004


class TestEmailPersonalization:
    """Test suite for EmailPersonalization model."""

    def test_str_method(self, email_personalization: EmailPersonalization):
        """Test string representation of EmailPersonalization."""
        expected = f"Personalization for Email [{email_personalization.email}]"
        assert str(email_personalization) == expected

    def test_email_relationship(self, email_personalization: EmailPersonalization):
        """Test email one-to-one relationship."""
        assert email_personalization.email is not None
        assert isinstance(email_personalization.email, Email)

    def test_get_user(self, email_personalization: EmailPersonalization):
        """Test get_user method returns user from email's folder's account."""
        user = email_personalization.get_user()
        assert user is not None
        assert user == email_personalization.email.folder.account.user

    def test_one_to_one_with_email(self, db):
        """Test one-to-one relationship with Email."""
        email = EmailFactory()
        personalization = EmailPersonalizationFactory(email=email)

        # Access through reverse relation
        assert email.personalization == personalization

    def test_notes_can_be_blank(self, db):
        """Test that notes field can be blank."""
        personalization = EmailPersonalizationFactory(notes="")
        assert personalization.notes == ""

    def test_importance_level_nullable(self, db):
        """Test that importance_level can be null."""
        personalization = EmailPersonalizationFactory(importance_level=None)
        assert personalization.importance_level is None

    def test_tags_manager(self, email_personalization: EmailPersonalization):
        """Test tags manager is available."""
        assert hasattr(email_personalization, "tags")

    def test_adding_tags(self, db):
        """Test adding tags to email personalization."""
        personalization = EmailPersonalizationFactory()
        user = personalization.get_user()

        # Manually create UserTags with the user
        from django_overtuned.user_tags.models import UserTag

        tag1 = UserTag.objects.create(name="urgent", user=user)
        tag2 = UserTag.objects.create(name="work", user=user)
        tag3 = UserTag.objects.create(name="important", user=user)

        personalization.tags.add(tag1, tag2, tag3)

        assert personalization.tags.count() == 3  # noqa: PLR2004
        tag_names = [tag.name for tag in personalization.tags.all()]
        assert "urgent" in tag_names
        assert "work" in tag_names
        assert "important" in tag_names


class TestEmailFolderPersonalization:
    """Test suite for EmailFolderPersonalization model."""

    def test_str_method(self, email_folder_personalization: EmailFolderPersonalization):
        """Test string representation of EmailFolderPersonalization."""
        expected = f"Personalization for Folder [{email_folder_personalization.folder}]"
        assert str(email_folder_personalization) == expected

    def test_folder_relationship(
        self,
        email_folder_personalization: EmailFolderPersonalization,
    ):
        """Test folder one-to-one relationship."""
        assert email_folder_personalization.folder is not None
        assert isinstance(email_folder_personalization.folder, EmailFolder)

    def test_get_user(self, email_folder_personalization: EmailFolderPersonalization):
        """Test get_user method returns user from folder's account."""
        user = email_folder_personalization.get_user()
        assert user is not None
        assert user == email_folder_personalization.folder.account.user

    def test_one_to_one_with_folder(self, db):
        """Test one-to-one relationship with EmailFolder."""
        folder = EmailFolderFactory()
        personalization = EmailFolderPersonalizationFactory(folder=folder)

        # Access through reverse relation
        assert folder.personalization == personalization

    def test_display_color_can_be_blank(self, db):
        """Test that display_color can be blank."""
        personalization = EmailFolderPersonalizationFactory(display_color="")
        assert personalization.display_color == ""

    def test_display_color_format(
        self,
        email_folder_personalization: EmailFolderPersonalization,
    ):
        """Test that display_color follows HEX format."""
        if email_folder_personalization.display_color:
            assert email_folder_personalization.display_color.startswith("#")
            assert len(email_folder_personalization.display_color) == 7  # noqa: PLR2004

    def test_display_name_can_be_blank(self, db):
        """Test that display_name can be blank."""
        personalization = EmailFolderPersonalizationFactory(display_name="")
        assert personalization.display_name == ""

    def test_tags_manager(
        self,
        email_folder_personalization: EmailFolderPersonalization,
    ):
        """Test tags manager is available."""
        assert hasattr(email_folder_personalization, "tags")

    def test_adding_tags(self, db):
        """Test adding tags to folder personalization."""
        personalization = EmailFolderPersonalizationFactory()
        user = personalization.get_user()

        # Manually create UserTags with the user
        from django_overtuned.user_tags.models import UserTag

        tag1 = UserTag.objects.create(name="work", user=user)
        tag2 = UserTag.objects.create(name="archive", user=user)
        tag3 = UserTag.objects.create(name="important", user=user)

        personalization.tags.add(tag1, tag2, tag3)

        assert personalization.tags.count() == 3  # noqa: PLR2004
        tag_names = [tag.name for tag in personalization.tags.all()]
        assert "work" in tag_names
        assert "archive" in tag_names
        assert "important" in tag_names
