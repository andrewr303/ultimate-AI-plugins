import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://www.example.com"),
  title: { default: "Example Widgets", template: "%s | Example Widgets" },
  description: "Synthetic fixture layout for stack detection tests.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
