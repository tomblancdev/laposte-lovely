import { ValueOf } from "next/dist/shared/lib/constants";
import { components } from "@/types/auth";

export function parseErrors<T extends readonly string[]>(
	fields: T,
	errors?:
		| {
				code: string;
				message: number;
				param?: string;
		  }[]
		| undefined,
): {
	global?: string[];
	fields?: Record<(typeof fields)[number], string[]>;
} {
	if (!errors) return {};

	const fieldErrors: Record<string, string[]> = {};
	const globalErrors: string[] = [];

	errors.forEach((error) => {
		if (error.param) {
			if (!fieldErrors[error.param]) {
				fieldErrors[error.param] = [];
			}
			fieldErrors[error.param]?.push(String(error.message));
		} else {
			globalErrors.push(String(error.message));
		}
	});

	return {
		global: globalErrors.length > 0 ? globalErrors : undefined,
		fields: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
	};
}

type FlowId =
	| "login"
	| "mfa_authenticate"
	| "mfa_reauthenticate"
	| "provider_redirect"
	| "provider_signup"
	| "provider_token"
	| "reauthenticate"
	| "signup"
	| "verify_email"
	| "verify_phone";

export function getCurrentFlowStep(
	flows: {
		id: FlowId;
		is_pending?: true;
		provider?: components["schemas"]["Provider"];
	}[],
):
	| {
			id: FlowId;
			is_pending?: true;
			provider?: components["schemas"]["Provider"];
	  }
	| undefined {
	const flow = flows.find((flow) => flow.is_pending);
	if (flow) {
		return flow;
	}
	return;
}

export const flowMessages: Record<FlowId, string> = {
	login: "You need to log in to continue",
	mfa_authenticate: "You need to authenticate to continue",
	mfa_reauthenticate: "You need to reauthenticate to continue",
	provider_redirect: "You need to log in to continue",
	provider_signup: "You need to sign up to continue",
	provider_token: "You need to log in to continue",
	reauthenticate: "You need to reauthenticate to continue",
	signup: "You need to sign up to continue",
	verify_email:
		"You need to verify your email to continue. If you lost the email, please reset password",
	verify_phone:
		"You need to verify your phone to continue. If you lost the code please reset password",
};
