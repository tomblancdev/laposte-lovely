import PasswordResetForm from "@/app/ui/auth/password-reset-form";

export default async function ResetPasswordPage({
	params,
}: {
	params: Promise<{ key: string }>;
}) {
	const { key } = await params;
	// parse the key
	const parsed_key = decodeURIComponent(key);

	return (
		<div className="flex flex-col items-center justify-center gap-2 h-screen">
			<h1 className="text-2xl font-bold">Reset Password</h1>
			<p className="text-sm text-muted-foreground">Reset your password</p>
			<div className="w-full max-w-sm">
				<PasswordResetForm token={parsed_key} />
			</div>
		</div>
	);
}
