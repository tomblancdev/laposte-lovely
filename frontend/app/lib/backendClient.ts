import createClient from "openapi-fetch";
import { paths as authpats } from "@/types/auth";
import { paths as overtuned } from "@/types/django-overtuned";

export const authClient = createClient<authpats>({
	baseUrl: process.env.BACKEND_INTERNAL_URL,
});

export const clientOvertuned = createClient<overtuned>({
	baseUrl: process.env.BACKEND_INTERNAL_URL,
	// @ts-ignore
	headers: {
		"Content-Type": "application/json",
		Accept: "application/json",
	},
});
