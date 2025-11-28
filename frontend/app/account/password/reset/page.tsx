"use server";
import PasswordResetRequestForm from "@/app/ui/auth/password-reset-request-form";
import GoBackButton from "@/app/ui/go-back-button";

export default async function ResetPasswordPage() {
	return (
		<div className="flex flex-col items-center justify-center gap-2 h-screen">
			<h1 className="text-2xl font-bold">Reset Password</h1>
			<p className="text-sm text-muted-foreground">
				Enter your email to reset your password.
			</p>
			<div className="w-full max-w-sm">
				<PasswordResetRequestForm />
			</div>
			<GoBackButton />
		</div>
	);
}
