import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const users = [
  { username: "olarust", password: "123123", name: "Ola" },
  { username: "tess", password: "123123", name: "Therese" },
];

export async function POST(request: Request) {
  const { username, password } = await request.json();

  const user = users.find(
    (u) => u.username === username && u.password === password
  );

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const cookieStore = await cookies();
  cookieStore.set("session", JSON.stringify({ username: user.username, name: user.name }), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 1 uke
  });

  return NextResponse.json({ ok: true });
}
