"use server";

import "server-only";
import { jwtVerify, SignJWT } from "jose";
import { cookies } from "next/headers";
import type { SessionPayload } from "@/app/lib/auth/definitions";
import { authClient } from "../backendClient";

const secretKey = process.env.SESSION_SECRET;
const encodedKey = new TextEncoder().encode(secretKey);

export async function encrypt(payload: SessionPayload) {
	return new SignJWT(payload)
		.setProtectedHeader({ alg: "HS256" })
		.setIssuedAt()
		.setExpirationTime("7d")
		.sign(encodedKey);
}

export async function decrypt(session: string | undefined = "") {
	try {
		const { payload } = await jwtVerify<SessionPayload>(session, encodedKey, {
			algorithms: ["HS256"],
		});
		return payload;
	} catch (error) {
		return null;
	}
}

export async function createSession(authToken: string) {
	const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
	const session = await encrypt({ authToken });
	const cookieStore = await cookies();

	cookieStore.set("session", session, {
		httpOnly: true,
		secure: true,
		expires: expiresAt,
		sameSite: "lax",
		path: "/",
	});
}

export async function updateSession() {
	const session = (await cookies()).get("session")?.value;
	const payload = await decrypt(session);

	if (!session || !payload) {
		return null;
	}

	const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

	const cookieStore = await cookies();
	cookieStore.set("session", session, {
		httpOnly: true,
		secure: true,
		expires: expires,
		sameSite: "lax",
		path: "/",
	});
}

export async function deleteSession() {
	const cookie = (await cookies()).get("session")?.value;
	const session = await decrypt(cookie);
	// if the session is not valid, return null
	if (!session) {
		return null;
	}
	const response = await authClient.DELETE(
		"/api/auth/{client}/v1/auth/session",
		{
			params: {
				path: {
					client: "app",
				},
				headers: {
					"X-Session-Token": `${session.authToken}`,
				},
			},
		},
	);
	if (response.error) {
		if (response.error.status !== 401) {
			return null;
		}
	}
	const cookieStore = await cookies();
	cookieStore.delete("session");
}
