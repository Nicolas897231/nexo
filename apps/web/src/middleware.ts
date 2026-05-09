import { NextResponse, type NextRequest } from "next/server";

const privatePrefixes = [
  "/dashboard",
  "/onboarding",
  "/movements",
  "/goals",
  "/simulators",
  "/rules",
  "/reports",
  "/settings",
  "/notifications",
];

export function middleware(request: NextRequest) {
  const isPrivate = privatePrefixes.some((prefix) => request.nextUrl.pathname.startsWith(prefix));
  if (!isPrivate) return NextResponse.next();
  const hasSession = request.cookies.has("access_token");
  if (!hasSession) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
