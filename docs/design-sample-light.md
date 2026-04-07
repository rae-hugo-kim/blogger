<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<style>
        body {
            font-family: 'Space Grotesk', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 24;
            vertical-align: middle;
        }
    </style>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "on-secondary-container": "#8fc0cc",
                        "on-surface": "#131313",
                        "on-tertiary-fixed": "#2a1800",
                        "surface-variant": "#f4f4f4",
                        "on-surface-variant": "#5a6a6e",
                        "outline-variant": "#dee4e6",
                        "on-background": "#131313",
                        "inverse-on-surface": "#f4f4f4",
                        "on-tertiary": "#462b00",
                        "primary-fixed": "#a2eeff",
                        "surface-container-high": "#f9f9f9",
                        "inverse-surface": "#131313",
                        "surface-container-lowest": "#FFFFFF",
                        "on-error": "#690005",
                        "secondary-fixed": "#b8ebf7",
                        "on-tertiary-container": "#6e4600",
                        "secondary-container": "#e0f2f7",
                        "inverse-primary": "#006877",
                        "on-tertiary-fixed-variant": "#643f00",
                        "on-primary-fixed": "#001f25",
                        "surface": "#FFFFFF",
                        "on-error-container": "#ffdad6",
                        "surface-bright": "#FFFFFF",
                        "surface-container-low": "#fafafa",
                        "on-primary-container": "#00363e",
                        "surface-tint": "#22d3ee",
                        "surface-dim": "#f2f2f2",
                        "error": "#ba1a1a",
                        "primary-fixed-dim": "#22d3ee",
                        "on-secondary-fixed-variant": "#184d57",
                        "secondary": "#3f636b",
                        "primary-container": "#22d3ee",
                        "tertiary-fixed": "#ffddb5",
                        "primary": "#006877",
                        "on-secondary": "#ffffff",
                        "secondary-fixed-dim": "#9dcfda",
                        "on-primary": "#ffffff",
                        "tertiary-fixed-dim": "#ffb957",
                        "surface-container": "#f4f4f4",
                        "on-primary-fixed-variant": "#004e5a",
                        "on-secondary-fixed": "#001f25",
                        "tertiary-container": "#ffb13b",
                        "surface-container-highest": "#e2e2e2",
                        "background": "#FFFFFF",
                        "tertiary": "#7d5800",
                        "error-container": "#93000a",
                        "outline": "#70797b"
                    },
                    "borderRadius": {
                        "DEFAULT": "0px",
                        "lg": "0px",
                        "xl": "0px",
                        "full": "9999px"
                    },
                    "fontFamily": {
                        "headline": ["Space Grotesk"],
                        "body": ["Space Grotesk"],
                        "label": ["Space Grotesk"]
                    }
                },
            },
        }
    </script>
</head>
<body class="bg-surface text-on-surface">
<!-- TopAppBar -->
<header class="bg-[#FFFFFF] dark:bg-[#131313] docked full-width top-0 no-line tonal-shift via-negative-space flat no shadows fixed w-full z-50">
<nav class="flex justify-between items-center w-full px-6 py-8 max-w-[800px] mx-auto">
<div class="text-xl font-bold tracking-tighter text-black dark:text-white font-['Space_Grotesk']">
                BLOWFISH
            </div>
<div class="hidden md:flex gap-8 items-center font-['Space_Grotesk'] text-base tracking-normal">
<a class="text-cyan-400 border-b-2 border-cyan-400 pb-1 hover:text-cyan-400 transition-colors duration-200" href="#">Posts</a>
<a class="text-black dark:text-white hover:text-cyan-400 transition-colors duration-200" href="#">Projects</a>
<a class="text-black dark:text-white hover:text-cyan-400 transition-colors duration-200" href="#">About</a>
</div>
<div class="flex items-center gap-4 text-black dark:text-white">
<span class="material-symbols-outlined cursor-pointer hover:text-cyan-400 transition-colors duration-200" data-icon="light_mode">light_mode</span>
<span class="material-symbols-outlined cursor-pointer hover:text-cyan-400 transition-colors duration-200" data-icon="rss_feed">rss_feed</span>
</div>
</nav>
</header>
<main class="pt-32 pb-24 px-6 max-w-[800px] mx-auto">
<!-- Hero Post Section -->
<section class="mb-24">
<div class="relative w-full aspect-[16/9] mb-8 bg-surface-container-low overflow-hidden">
<img alt="Hero" class="w-full h-full object-cover filter grayscale hover:grayscale-0 transition-all duration-700" data-alt="Abstract 3D render of geometric crystalline structures in a dark void with neon cyan glowing edges and sharp technical precision" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDxXpsQKODyJ42hHqiU_WKRhiJ4ZvoJT0yZyIkl1VhIDD65qjVagVgJsRJY5hbxii_7NORz4qjQ-DApRFEwgAFmDBztDKqk4x9omSeEFwdA7o-GvTzp6teN3zS2bugvH7Y5MkTPkZ38gqWje0k9WNfSgbrPFYxE-CKREU2zKEQlWFgf5MhKd1HHJMZqvLX-TGjwHnYEtA6N38u6iYTExZ1OFKJToRW-VpKMUcpUnY_PoYU0_UJVJYBKEEk9-Q-di_CN0fEuLrF-Z4g"/>
</div>
<div class="space-y-4">
<div class="flex items-center gap-4">
<span class="text-[0.75rem] uppercase tracking-widest font-medium text-primary-container">Featured</span>
<span class="text-[0.75rem] uppercase tracking-widest text-on-surface-variant">March 24, 2024</span>
</div>
<h1 class="text-[3.5rem] font-bold leading-[1.1] tracking-[-0.02em] text-on-surface">
                    The Architecture of Decenteralized Systems.
                </h1>
<p class="text-[1.125rem] text-on-surface-variant leading-relaxed max-w-[640px]">
                    Exploring the intersection of high-performance computing and minimalist design principles in the modern web era.
                </p>
<div class="pt-4">
<a class="inline-flex items-center gap-2 text-[0.75rem] uppercase tracking-widest font-bold text-primary-container group" href="#">
                        Read Manuscript 
                        <span class="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform" data-icon="arrow_forward">arrow_forward</span>
</a>
</div>
</div>
</section>
<!-- Recent Articles List -->
<section class="space-y-20">
<div class="flex justify-between items-end border-b-2 border-surface-container-highest pb-4">
<h2 class="text-[1.75rem] font-semibold tracking-tight">Recent Articles</h2>
<span class="text-[0.75rem] uppercase tracking-widest text-on-surface-variant">Archive / 2024</span>
</div>
<!-- Article 1 -->
<article class="group cursor-pointer">
<div class="flex flex-col md:flex-row gap-8 items-start">
<div class="w-full md:w-1/3 aspect-[4/3] bg-surface-container-low overflow-hidden">
<img alt="Article" class="w-full h-full object-cover filter grayscale group-hover:grayscale-0 transition-all duration-500" data-alt="Macro photography of integrated circuit board with glowing cyan micro-leds and sharp metallic textures" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAt1e4YtqelGkXPCtkThxfb7vaSHSm_aAGDjJ0J_zp-CdVja9AYnO_LMZHe_kNkYH7kvpqMQUxigIBEtx4MqS2hETsH-QZ5uaXJUSMKfXE1FkE6TFBJ-Vg4Fkv--8JHId2oOhAKuw3O5NjgCatZ0dzUH7Zq-KTnBJhp2Dqp915xxQAgJX1_66k3h7Ud3o2slm1LEfBKk1Yat1VsLYUFt1Ey9D0EjiuHkjV2OQfEIm9iFCjQXPLcQXnvzQegJp1CcsUMbe3rVQsd-Ig"/>
</div>
<div class="flex-1 space-y-3">
<span class="text-[0.75rem] uppercase tracking-widest text-on-surface-variant">Feb 12, 2024</span>
<h3 class="text-[1.5rem] font-semibold tracking-tight group-hover:text-primary-container transition-colors">
                            The Ghost in the Machine: Minimalist Code.
                        </h3>
<p class="text-on-surface-variant leading-relaxed">
                            How stripping back complexity in our logic leads to more resilient and maintainable digital structures.
                        </p>
<div class="flex gap-2 pt-2">
<span class="px-3 py-1 bg-surface-container-high text-[0.65rem] uppercase tracking-tighter font-bold text-primary-container">Engineering</span>
<span class="px-3 py-1 bg-surface-container-high text-[0.65rem] uppercase tracking-tighter font-bold text-primary-container">Performance</span>
</div>
</div>
</div>
</article>
<!-- Article 2 -->
<article class="group cursor-pointer">
<div class="flex flex-col md:flex-row gap-8 items-start">
<div class="w-full md:w-1/3 aspect-[4/3] bg-surface-container-low overflow-hidden">
<img alt="Article" class="w-full h-full object-cover filter grayscale group-hover:grayscale-0 transition-all duration-500" data-alt="Electronic components arranged in a neat grid pattern on a stark white background with hard shadows" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB8L4fF-z7OJ6v1vpxiVaP6JK0g1XlDleBaQb8rdJesRf9OD0cEQCj7LZIsZP6pD1z9O_hY4SmMReWrbVey5v8yYsg5-xeCCxVNKLEOVVcoS4G_kagqtIcCT34ju_dxZ2mDXZX6HZjT6cuMbKC9w2f2I1LYIroHIVFI1MyrxB-J8s0GHGJe-OY10dzdBAR4W8At0Br2S6eaGfj5H33zBeo5ESpdwp4kEJUdqIMvD8u5SOD86aiBCgJH_SP4raGysvncvv3H7FW5HT4"/>
</div>
<div class="flex-1 space-y-3">
<span class="text-[0.75rem] uppercase tracking-widest text-on-surface-variant">Jan 28, 2024</span>
<h3 class="text-[1.5rem] font-semibold tracking-tight group-hover:text-primary-container transition-colors">
                            Typography as a Service.
                        </h3>
<p class="text-on-surface-variant leading-relaxed">
                            Why the choice of font defines the technical authority of your documentation more than the content itself.
                        </p>
<div class="flex gap-2 pt-2">
<span class="px-3 py-1 bg-surface-container-high text-[0.65rem] uppercase tracking-tighter font-bold text-primary-container">Design</span>
<span class="px-3 py-1 bg-surface-container-high text-[0.65rem] uppercase tracking-tighter font-bold text-primary-container">Editorial</span>
</div>
</div>
</div>
</article>
<!-- Article 3 -->
<article class="group cursor-pointer">
<div class="flex flex-col md:flex-row gap-8 items-start">
<div class="w-full md:w-1/3 aspect-[4/3] bg-surface-container-low overflow-hidden">
<img alt="Article" class="w-full h-full object-cover filter grayscale group-hover:grayscale-0 transition-all duration-500" data-alt="Digital representation of earth's data network with interconnected points of cyan light on a dark blueprint style background" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBxcdckFxdyaCybsLkC6VHDmIwbs8Z6gctb8IEIDAjfSiQ7WwrfDRtDopr5mSDZ1AZ5FRcSbNYLtD_jhp5ZaTw98c1gIvUanGnPmYXSgHKY8xzH7j--ABPBtJT7A0GSXWEGznrlGjcbaOaQb-66ybFrMXNIx8gTaREFbHtG7LfPdh97gdD3_UxH6x4Dg-uv_1SZInCuRl8UFQ_T-x0hFta1nmzjlbtqaGmO2zCG_q7DgXlSQCR_2O26imEHmD38D4dUOaGL1wX82XM"/>
</div>
<div class="flex-1 space-y-3">
<span class="text-[0.75rem] uppercase tracking-widest text-on-surface-variant">Jan 05, 2024</span>
<h3 class="text-[1.5rem] font-semibold tracking-tight group-hover:text-primary-container transition-colors">
                            The Static Site Renaissance.
                        </h3>
<p class="text-on-surface-variant leading-relaxed">
                            Returning to our roots with Hugo and the power of pre-rendered interfaces for the future.
                        </p>
<div class="flex gap-2 pt-2">
<span class="px-3 py-1 bg-surface-container-high text-[0.65rem] uppercase tracking-tighter font-bold text-primary-container">Web Dev</span>
<span class="px-3 py-1 bg-surface-container-high text-[0.65rem] uppercase tracking-tighter font-bold text-primary-container">Speed</span>
</div>
</div>
</div>
</article>
</section>
<!-- Newsletter Subscription (Editorial Style) -->
<section class="mt-32 p-12 bg-surface-container-low">
<div class="max-w-[500px] mx-auto text-center space-y-6">
<h4 class="text-[1.125rem] font-bold uppercase tracking-widest">Subscribe to the Log</h4>
<p class="text-on-surface-variant text-sm">Monthly insights on technical design, high-performance web systems, and editorial aesthetics.</p>
<div class="flex flex-col gap-4">
<input class="bg-transparent border-0 border-b-2 border-outline-variant focus:ring-0 focus:border-primary-container font-label uppercase text-[0.75rem] tracking-widest p-2 text-center" placeholder="ENTER EMAIL ADDRESS" type="email"/>
<button class="bg-primary-container text-on-primary font-bold py-4 uppercase tracking-widest text-[0.75rem] hover:bg-on-secondary-container transition-colors">
                        Register Interest
                    </button>
</div>
</div>
</section>
</main>
<!-- Footer -->
<footer class="bg-[#FFFFFF] dark:bg-[#131313] full-width bottom-0 no-line tonal-shift flat no shadows border-t border-surface-container-highest">
<div class="flex flex-col md:flex-row justify-between items-center w-full px-6 py-12 max-w-[800px] mx-auto gap-4">
<div class="text-sm font-bold text-black dark:text-white font-['Space_Grotesk'] uppercase tracking-widest">
                © 2024 BLOWFISH
            </div>
<div class="flex gap-6 font-['Space_Grotesk'] text-xs uppercase tracking-widest">
<a class="text-gray-500 dark:text-gray-400 hover:text-cyan-400 transition-colors duration-200 Active: underline underline-offset-4" href="#">GitHub</a>
<a class="text-gray-500 dark:text-gray-400 hover:text-cyan-400 transition-colors duration-200 Active: underline underline-offset-4" href="#">Twitter</a>
<a class="text-gray-500 dark:text-gray-400 hover:text-cyan-400 transition-colors duration-200 Active: underline underline-offset-4" href="#">Hugo</a>
<a class="text-gray-500 dark:text-gray-400 hover:text-cyan-400 transition-colors duration-200 Active: underline underline-offset-4" href="#">Blowfish</a>
</div>
</div>
</footer>
</body></html>