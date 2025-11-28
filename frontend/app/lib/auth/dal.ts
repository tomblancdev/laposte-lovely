import "server-only";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { cache } from "react";
import { decrypt } from "@/app/lib/auth/session";
import { authClient } from "../backendClient";

export const verifySession = cache(async (redirectToLogin = true) => {
	const cookie = (await cookies()).get("session")?.value;
	const session = await decrypt(cookie);

	if (!session?.authToken) {
		if (redirectToLogin) {
			redirect("/");
		}
		return null;
	}

	return { isAuth: true, authToken: session.authToken };
});

export const getUser = cache(async (redirectToLogin = true) => {
	const session = await verifySession(redirectToLogin);
	if (!session) return null;

	try {
		const response = await authClient.GET(
			"/api/auth/{client}/v1/auth/session",
			{
				params: {
					path: {
						client: "app",
					},
				},
				headers: {
					"X-Session-Token": `${session.authToken}`,
				},
			},
		);
		if (response.error) {
			return null;
		}
		const user = response.data;

		return user;
	} catch (error) {
		return null;
	}
});
