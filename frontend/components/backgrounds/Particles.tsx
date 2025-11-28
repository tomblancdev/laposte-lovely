"use client";

import { useEffect, useRef } from "react";

class Particle {
	x: number;
	y: number;
	radius: number;
	color: string;
	speedX: number;
	speedY: number;
	constructor(x: number, y: number, radius: number, color: string) {
		this.x = x;
		this.y = y;
		this.radius = radius;
		this.color = color;
		this.speedX = Math.random() * 2 - 1;
		this.speedY = Math.random() * 2 - 1;
	}

	draw(context: CanvasRenderingContext2D) {
		context.beginPath();
		context.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
		context.fillStyle = this.color;
		context.fill();
	}

	update(canvas: HTMLCanvasElement) {
		if (this.x + this.radius > canvas.width || this.x - this.radius < 0) {
			this.speedX = -this.speedX;
		}
		if (this.y + this.radius > canvas.height || this.y - this.radius < 0) {
			this.speedY = -this.speedY;
		}
		this.x += this.speedX;
		this.y += this.speedY;
	}
}

export default function Background({
	...props
}: React.ComponentProps<"canvas">) {
	const canvas = useRef<HTMLCanvasElement>(null);

	useEffect(() => {
		const ctx = canvas.current?.getContext("2d");
		if (!ctx) return;
		if (!canvas.current) return;

		canvas.current.width = window.innerWidth;
		canvas.current.height = window.innerHeight;

		const particles: Particle[] = [];
		// get colors using css vars --primary, --secondary, --tertiary
		const colors = [
			getComputedStyle(document.documentElement).getPropertyValue("--primary"),
			getComputedStyle(document.documentElement).getPropertyValue(
				"--secondary",
			),
			getComputedStyle(document.documentElement).getPropertyValue("--tertiary"),
		];

		for (let i = 0; i < 100; i++) {
			const radius = Math.random() * 10 + 5;
			const x = Math.random() * canvas.current.width;
			const y = Math.random() * canvas.current.height;
			const color = colors[Math.floor(Math.random() * colors.length)];
			if (!color) continue;
			particles.push(new Particle(x, y, radius, color));
		}

		function animate() {
			if (!ctx) return;
			ctx.fillStyle = "rgba(0, 0, 0, 0)";
			ctx.globalCompositeOperation = "lighter";
			ctx.globalAlpha = 0.5;
			if (!canvas.current) return;
			ctx.fillRect(0, 0, canvas.current.width, canvas.current.height);
			ctx.clearRect(0, 0, canvas.current.width, canvas.current.height);
			particles.forEach((particle) => {
				if (!canvas.current) return;
				particle.update(canvas.current);
				particle.draw(ctx);
			});
			requestAnimationFrame(animate);
		}

		animate();
	}, []);

	useEffect(() => {
		const handleResize = () => {
			if (canvas.current) {
				canvas.current.width = window.innerWidth;
				canvas.current.height = window.innerHeight;
			}
		};

		window.addEventListener("resize", handleResize);
		handleResize();

		return () => {
			window.removeEventListener("resize", handleResize);
		};
	}, []);

	return (
		<canvas
			id="canvas"
			ref={canvas}
			{...props}
			className="absolute top-0 left-0 -z-50"
		/>
	);
}
