import { verifyEmail } from "@/app/account/actions/auth";
import SignInForm from "@/app/ui/auth/signin-form";

function EmailValidated() {
	return (
		<div className="flex flex-col items-center justify-center h-screen">
			<h1 className="text-2xl font-bold">Email Verified</h1>
			<p className="text-gray-500">
				Your email has been successfully verified. You can now login !
			</p>
			<SignInForm />
		</div>
	);
}

function InvalidToken() {
	return (
		<div className="flex flex-col items-center justify-center h-screen">
			<h1 className="text-2xl font-bold text-red-500">Invalid Token</h1>
		</div>
	);
}

export default async function VerifyEmailPage({
	params,
}: {
	params: Promise<{ token: string }>;
}) {
	const { token } = await params;
	const emailValid = await verifyEmail(token);
	return (
		<div className="flex flex-col items-center justify-center h-screen">
			{emailValid ? <EmailValidated /> : <InvalidToken />}
		</div>
	);
}
