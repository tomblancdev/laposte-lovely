import { z } from "zod";

export const SigninFormSchema = z.object({
	email: z.string().email(),
	password: z.string(),
});

export const SignupFormSchema = z
	.object({
		email: z.string().email(),
		password: z.string(),
		confirm: z.string(),
	})
	.refine((data) => data.password === data.confirm, {
		message: "Passwords don't match",
	});

export type SessionPayload = {
	authToken: string;
};

export type EmailValidationPayload = {
	valid: boolean;
	message: string;
	errors?: string[];
};

export type FormState<T extends readonly string[]> =
	| {
			errors?: {
				fields?: Record<T[number], string[] | undefined>;
				global?: string[];
				flow?: {
					id: string;
					is_pending?: true;
					provider?:
						| {
								client_id?: string;
								flows: ("provider_redirect" | "provider_token")[];
								id: string;
								name: string;
								openid_configuration_url?: string;
						  }
						| undefined;
				};
			};
			message?: string;
	  }
	| undefined;
