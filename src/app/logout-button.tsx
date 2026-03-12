"use client";

import { useRouter } from "next/navigation";

export default function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    await fetch("/api/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  }

  return (
    <button
      onClick={handleLogout}
      style={{
        padding: "0.4rem 1rem",
        borderRadius: "4px",
        border: "1px solid #ccc",
        backgroundColor: "white",
        cursor: "pointer",
      }}
    >
      Logg ut
    </button>
  );
}
