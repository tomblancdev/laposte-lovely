"use client";

import Link from "next/link";
import { useActionState } from "react";
import { resetPassword } from "@/app/account/actions/auth";

export default function PasswordResetForm({
	extraContent,
	token,
}: {
	extraContent?: React.ReactNode;
	token: string;
}) {
	const [formState, action, pending] = useActionState(resetPassword, undefined);

	if (formState?.message) {
		return (
			<div className="flex flex-col w-full gap-4 border border-solid border-black/[.08] dark:border-white/[.145] rounded-lg p-8 sm:p-10 bg-white/[.05] dark:bg-white/[.06] backdrop-blur-md">
				<p className="text-success text-center">{formState.message}</p>
				<p className="text-muted-foreground text-center">
					You can now login with your new password.
				</p>
				<Link
					className=" grow rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
					href="/"
					type="button"
				>
					Login
				</Link>
			</div>
		);
	}

	return (
		<form
			className="flex flex-col w-full gap-4 border border-solid border-black/[.08] dark:border-white/[.145] rounded-lg p-8 sm:p-10 bg-white/[.05] dark:bg-white/[.06] backdrop-blur-md"
			action={action}
		>
			{formState?.errors?.global && (
				<div>
					{formState.errors.global.map((error) => (
						<p key={error} className="text-error">
							{error}
						</p>
					))}
				</div>
			)}
			{formState?.errors?.fields?.token && (
				<div>
					{formState.errors.fields.token.map((error) => (
						<p key={error} className="text-error">
							{error}
						</p>
					))}
				</div>
			)}
			<div className="flex flex-col gap-2">
				<label htmlFor="password">New Password</label>
				<input
					className="border border-solid border-black/[.08] dark:border-white/[.145] rounded-lg p-2 sm:p-4 bg-white/[.05] dark:bg-white/[.06]"
					id="password"
					name="password"
					type="password"
					placeholder="New Password"
				/>
			</div>
			{formState?.errors?.fields?.password && (
				<div>
					{formState.errors.fields.password.map((error) => (
						<p key={error} className="text-error">
							{error}
						</p>
					))}
				</div>
			)}
			<div className="flex flex-col gap-2">
				<label htmlFor="confirm">Confirm Password</label>
				<input
					className="border border-solid border-black/[.08] dark:border-white/[.145] rounded-lg p-2 sm:p-4 bg-white/[.05] dark:bg-white/[.06]"
					id="confirm"
					name="confirm"
					type="password"
					placeholder="Confirm Password"
				/>
			</div>
			{formState?.errors?.fields?.confirm && (
				<div>
					{formState.errors.fields.confirm.map((error) => (
						<p key={error} className="text-error">
							{error}
						</p>
					))}
				</div>
			)}
			<input type="hidden" name="key" value={token} />
			<button
				className=" grow rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
				disabled={pending}
				type="submit"
			>
				Reset Password
			</button>
			{extraContent}
		</form>
	);
}
