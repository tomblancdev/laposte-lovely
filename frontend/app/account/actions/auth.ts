"use server";

import { redirect } from "next/navigation";
import { z } from "zod";
import {
	type FormState,
	SigninFormSchema,
	SignupFormSchema,
} from "../../lib/auth/definitions";
import { createSession, deleteSession } from "../../lib/auth/session";
import {
	flowMessages,
	getCurrentFlowStep,
	parseErrors,
} from "../../lib/auth/utils";
import { authClient } from "../../lib/backendClient";

export async function login(
	state: FormState<["email", "password"]>,
	formData: FormData,
): Promise<FormState<["email", "password"]>> {
	// Validate form fields
	const validatedFields = SigninFormSchema.safeParse({
		email: formData.get("email"),
		password: formData.get("password"),
	});

	if (!validatedFields.success) {
		return {
			errors: {
				fields: {
					email: validatedFields.error.flatten().fieldErrors.email,
					password: validatedFields.error.flatten().fieldErrors.password,
				},
				global: validatedFields.error.flatten().formErrors,
			},
		};
	}

	const { email, password } = validatedFields.data;

	const response = await authClient.POST("/api/auth/{client}/v1/auth/login", {
		body: {
			email,
			password,
			phone: "",
			username: "",
		},
		params: {
			path: {
				client: "app",
			},
		},
	});
	console.log(response);

	if (response.error) {
		if (response.error.status === 400) {
			const fields = ["email", "password"] as const;
			console.log(response.error.errors);
			const errors = parseErrors(fields, response.error.errors);
			console.log(errors);
			return {
				errors: {
					fields: errors.fields,
					global: errors.global,
				},
			};
		}
		if (response.error.status === 401) {
			const flow = getCurrentFlowStep(response.error.data.flows);
			console.log(flow);
			if (flow) {
				const message = flowMessages[flow.id];
				return {
					errors: {
						flow: {
							id: flow.id,
							is_pending: flow.is_pending,
							provider: flow.provider,
						},
						global: [message],
					},
				};
			}
		}
		return {
			errors: {
				global: ["Invalid username or password"],
			},
		};
	}

	const user = response.data;
	if (!user.meta.session_token) {
		return {
			errors: {
				global: ["Invalid username or password"],
			},
		};
	}
	await createSession(user.meta.session_token);
	redirect("/");
}

export async function verifyEmail(token: string): Promise<boolean> {
	// Parse the token
	const parsed_token = decodeURIComponent(token);
	const response = await authClient.POST(
		"/api/auth/{client}/v1/auth/email/verify",
		{
			params: {
				path: {
					client: "app",
				},
			},
			body: {
				key: parsed_token,
			},
		},
	);
	if (response.error) {
		if (response.error.status === 401) {
			if (!response.error.meta.is_authenticated) {
				return true;
			}
		}
		return false;
	}
	if (!response.data.meta.access_token) {
		return false;
	}
	await createSession(response.data.meta.access_token);
	redirect("/");
}

export async function signup(
	state: FormState<["email", "password", "confirm"]>,
	formData: FormData,
): Promise<FormState<["email", "password", "confirm"]>> {
	console.log("signup");
	const validatedFields = SignupFormSchema.safeParse({
		email: formData.get("email"),
		password: formData.get("password"),
		confirm: formData.get("confirm"),
	});
	console.log(validatedFields);

	if (!validatedFields.success) {
		return {
			errors: {
				fields: {
					email: validatedFields.error.flatten().fieldErrors.email,
					password: validatedFields.error.flatten().fieldErrors.password,
					confirm: validatedFields.error.flatten().fieldErrors.confirm,
				},
				global: validatedFields.error.flatten().formErrors,
			},
		};
	}

	const { email, password } = validatedFields.data;

	const response = await authClient.POST("/api/auth/{client}/v1/auth/signup", {
		params: {
			path: {
				client: "app",
			},
		},
		body: {
			email,
			password,
		},
	});
	console.log(response);
	if (response.error) {
		if (response.error.status === 400) {
			const fields = ["email", "password", "confirm"] as const;
			const errors = parseErrors(fields, response.error.errors);
			return {
				errors: {
					fields: errors.fields,
					global: errors.global,
				},
			};
		}
		if (response.error.status === 401) {
			const flow = getCurrentFlowStep(response.error.data.flows);
			if (flow) {
				const message = flowMessages[flow.id];
				return {
					errors: {
						flow: {
							id: flow.id,
							is_pending: flow.is_pending,
							provider: flow.provider,
						},
						global: [message],
					},
				};
			}
		}
		return {
			errors: {
				global: ["An unknown error occurred"],
			},
		};
	}
	const user = response.data;
	if (!user.meta.session_token) {
		return {
			errors: {
				global: ["An unknown error occurred"],
			},
		};
	}
	await createSession(user.meta.session_token);
	redirect("/");
}

export async function sendEmailValidation(
	state: FormState<["email"]>,
	formData: FormData,
): Promise<FormState<["email"]>> {
	const validatedFields = z
		.object({
			email: z.string().email(),
		})
		.safeParse({
			email: formData.get("email"),
		});

	if (!validatedFields.success) {
		return {
			errors: {
				fields: {
					email: validatedFields.error.flatten().fieldErrors.email,
				},
				global: validatedFields.error.flatten().formErrors,
			},
		};
	}

	const { email } = validatedFields.data;

	const response = await authClient.POST(
		"/api/auth/{client}/v1/account/email",
		{
			params: {
				path: {
					client: "app",
				},
			},
			body: {
				email,
			},
		},
	);
	if (response.error) {
		if (response.error.status === 400) {
			const fields = ["email"] as const;
			const errors = parseErrors(fields, response.error.errors);
			return {
				errors: {
					fields: errors.fields,
					global: errors.global,
				},
			};
		}
		return {
			errors: {
				global: ["An unknown error occurred"],
			},
		};
	}
}

export async function sendPasswordReset(
	state: FormState<["email"]>,
	formData: FormData,
): Promise<FormState<["email"]>> {
	const validatedFields = z
		.object({
			email: z.string().email(),
		})
		.safeParse({
			email: formData.get("email"),
		});

	if (!validatedFields.success) {
		return {
			errors: {
				fields: {
					email: validatedFields.error.flatten().fieldErrors.email,
				},
				global: validatedFields.error.flatten().formErrors,
			},
		};
	}

	const { email } = validatedFields.data;

	const response = await authClient.POST(
		"/api/auth/{client}/v1/auth/password/request",
		{
			params: {
				path: {
					client: "app",
				},
			},
			body: {
				email,
			},
		},
	);

	if (response.error) {
		if (response.error.status === 400) {
			const fields = ["email"] as const;
			const errors = parseErrors(fields, response.error.errors);
			return {
				errors: {
					fields: errors.fields,
					global: errors.global,
				},
			};
		}
		if (response.error.status === 401) {
			const flow = getCurrentFlowStep(response.error.data.flows);
			if (flow) {
				const message = flowMessages[flow.id];
				return {
					errors: {
						flow: {
							id: flow.id,
							is_pending: flow.is_pending,
							provider: flow.provider,
						},
						global: [message],
					},
				};
			}
		}
		return {
			errors: {
				global: ["An unknown error occurred"],
			},
		};
	}
	return {
		message: "Password reset email sent",
	};
}

export async function resetPassword(
	state: FormState<["password", "confirm", "token"]>,
	formData: FormData,
): Promise<FormState<["password", "confirm", "token"]>> {
	const validatedFields = z
		.object({
			password: z.string(),
			confirm: z.string(),
			key: z.string(),
		})
		.refine((data) => data.password === data.confirm, {
			message: "Passwords don't match",
		})
		.safeParse({
			password: formData.get("password"),
			confirm: formData.get("confirm"),
			key: formData.get("key"),
		});

	if (!validatedFields.success) {
		return {
			errors: {
				fields: {
					password: validatedFields.error.flatten().fieldErrors.password,
					confirm: validatedFields.error.flatten().fieldErrors.confirm,
					token: validatedFields.error.flatten().fieldErrors.key,
				},
				global: validatedFields.error.flatten().formErrors,
			},
		};
	}

	const { password } = validatedFields.data;

	const response = await authClient.POST(
		"/api/auth/{client}/v1/auth/password/reset",
		{
			params: {
				path: {
					client: "app",
				},
			},
			body: {
				key: validatedFields.data.key,
				password,
			},
		},
	);

	if (response.error) {
		if (response.error.status === 400) {
			const fields = ["password", "confirm", "token"] as const;
			const errors = parseErrors(fields, response.error.errors);
			return {
				errors: {
					fields: errors.fields,
					global: errors.global,
				},
			};
		}
		if (response.error.status === 401) {
			const flow = getCurrentFlowStep(response.error.data.flows);
			if (flow) {
				const message = flowMessages[flow.id];
				return {
					errors: {
						flow: {
							id: flow.id,
							is_pending: flow.is_pending,
							provider: flow.provider,
						},
						global: [message],
					},
				};
			}
			return {
				message: "Password reset successfully",
			};
		}
		return {
			errors: {
				global: ["An unknown error occurred"],
			},
		};
	}
	return {
		message: "Password reset successfully",
	};
}

export async function logout() {
	await deleteSession();
	redirect("/");
}
