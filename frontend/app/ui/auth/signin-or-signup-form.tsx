"use client";

import { useState } from "react";
import SignInForm from "@/app/ui/auth/signin-form";
import SignUpForm from "@/app/ui/auth/signup-form";

export default function SignInOrSignUpForm() {
	const [mode, setMode] = useState<"login" | "register">("login");

	const toggleMode = (e: React.MouseEvent) => {
		e.preventDefault();
		setMode(mode === "login" ? "register" : "login");
	};

	if (mode === "register") {
		return (
			<SignUpForm
				extraContent={
					<p>
						Already have an account?{" "}
						<button
							type="button"
							className="text-foreground underline cursor-pointer"
							onClick={toggleMode}
						>
							Login
						</button>
					</p>
				}
			/>
		);
	}
	return (
		<SignInForm
			extraContent={
				<p>
					Don't have an account?{" "}
					<button
						type="button"
						className="text-foreground underline cursor-pointer"
						onClick={toggleMode}
					>
						Register
					</button>
				</p>
			}
		/>
	);
}
