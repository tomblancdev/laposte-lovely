import type { Metadata } from "next";
import { Road_Rage, Roboto_Mono } from "next/font/google";
import "./globals.css";
import Background from "@/components/backgrounds/Particles";
import { getUser } from "./lib/auth/dal";

const roadRage = Road_Rage({
	subsets: ["latin"],
	weight: ["400"],
	variable: "--font-road-rage",
});

const robotoMono = Roboto_Mono({
	subsets: ["latin"],
	weight: ["400", "700"],
	variable: "--font-roboto-mono",
});

export const metadata: Metadata = {
	title: "Django Overtuned",
	description: "Your Overtuned django project 🔥",
};

export default async function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body className={`${roadRage.variable} ${robotoMono.variable}`}>
				{children}
				<Background />
			</body>
		</html>
	);
}
