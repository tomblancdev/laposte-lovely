import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	/* config options here */
	output: "standalone",
	logging: {
		fetches: {
			fullUrl: true,
			hmrRefreshes: true,
		},
	},
};

export default nextConfig;
