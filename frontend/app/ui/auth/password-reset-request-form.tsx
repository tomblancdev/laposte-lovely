"use client";

import { useActionState } from "react";
import { sendPasswordReset } from "@/app/account/actions/auth";

export default function PasswordResetRequestForm({
	extraContent,
}: {
	extraContent?: React.ReactNode;
}) {
	const [state, action, pending] = useActionState(sendPasswordReset, undefined);

	return (
		<form
			className="flex flex-col w-full gap-4 border border-solid border-black/[.08] dark:border-white/[.145] rounded-lg p-8 sm:p-10 bg-white/[.05] dark:bg-white/[.06] backdrop-blur-md"
			action={action}
		>
			{state?.errors?.global && (
				<div>
					{state.errors.global.map((error, index) => (
						<p key={error} className="text-error">
							{error}
						</p>
					))}
				</div>
			)}
			<div className="flex flex-col gap-2">
				<label htmlFor="email">Email</label>
				<input
					className="border border-solid border-black/[.08] dark:border-white/[.145] rounded-lg p-2 sm:p-4 bg-white/[.05] dark:bg-white/[.06]"
					id="email"
					name="email"
					placeholder="Email"
				/>
			</div>
			{state?.errors?.fields?.email && (
				<div>
					{state.errors.fields.email.map((error, index) => (
						<p key={error} className="text-error">
							{error}
						</p>
					))}
				</div>
			)}
			<button
				className=" grow rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
				disabled={pending}
				type="submit"
			>
				Send Validation Email
			</button>
			{extraContent}
		</form>
	);
}
