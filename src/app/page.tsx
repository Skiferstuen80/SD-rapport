import { cookies } from "next/headers";
import LogoutButton from "./logout-button";
import RueButton from "./rue-button";
import HmsReportPanel from "./hms-report-panel";

export default async function Home() {
  const cookieStore = await cookies();
  const session = cookieStore.get("session");
  const user = session ? JSON.parse(session.value) : null;

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <img src="/logo.svg" alt="Åge Haverstad AS" style={{ height: "45px", filter: "invert(1)" }} />
          <h1 style={{ margin: 0 }}>SD Rapport</h1>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <span>Hei, {user?.name}!</span>
          <LogoutButton />
        </div>
      </div>
      <RueButton />
      <hr style={{ margin: "2rem 0", border: "none", borderTop: "1px solid #e2e8f0" }} />
      <HmsReportPanel />
    </main>
  );
}
