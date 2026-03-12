import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SD Rapport",
  description: "SD Rapport - dashbord for data fra API",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="no">
      <body>{children}</body>
    </html>
  );
}
