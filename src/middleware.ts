import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const session = request.cookies.get("session");

  if (!session) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // Beskytt alt unntatt login-side, API-ruter og statiske filer
    "/((?!login|api|skjerm|_next/static|_next/image|favicon.ico).*)",
  ],
};
