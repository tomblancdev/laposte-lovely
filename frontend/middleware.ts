import { cookies } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";
import { decrypt } from "@/app/lib/auth/session";

// 1. Specify protected and public routes
const protectedRoutes: Array<string | ((path: string) => boolean)> = [];
const publicRoutes: Array<string | ((path: string) => boolean)> = [
	(path: string) => true,
];

function isPublicRoute(path: string): boolean {
	return publicRoutes.some((route) => {
		if (typeof route === "string") {
			return path === route;
		}
		if (typeof route === "function") {
			return route(path);
		}
		return false;
	});
}

function isProtectedRoute(path: string): boolean {
	return protectedRoutes.some((route) => {
		if (typeof route === "string") {
			return path === route;
		}
		if (typeof route === "function") {
			return route(path);
		}
		return false;
	});
}

function getRouteType(path: string): "protected" | "public" | undefined {
	if (isProtectedRoute(path)) {
		return "protected";
	}
	if (isPublicRoute(path)) {
		return "public";
	}
	return undefined;
}

export default async function middleware(req: NextRequest) {
	// 2. Check if the current route is protected or public
	const path = req.nextUrl.pathname;
	const routeType = getRouteType(path);

	if (routeType === "public") {
		return NextResponse.next();
	}

	// 3. Decrypt the session from the cookie
	const cookie = (await cookies()).get("session")?.value;
	const session = await decrypt(cookie);

	// 4. Redirect to /login if the user is not authenticated
	if (!session?.userId) {
		return NextResponse.redirect(new URL("/", req.nextUrl));
	}

	return NextResponse.next();
}

// Routes Middleware should not run on
export const config = {
	matcher: ["/((?!api|_next/static|_next/image|.*\\.png$).*)"],
};
