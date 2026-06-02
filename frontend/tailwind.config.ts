import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14161f",
        panel: "#ffffff",
        line: "#d9dee8",
        brand: "#155e75",
        accent: "#b45309"
      }
    }
  },
  plugins: []
};

export default config;
