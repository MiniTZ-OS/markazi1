export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col justify-center px-6 py-16 lg:px-10">
        <div className="max-w-3xl space-y-8">
          <span className="inline-flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-sm font-semibold uppercase tracking-[0.2em] text-slate-200 ring-1 ring-white/10">
            Trusted by visionary brands
          </span>
          <h1 className="text-5xl font-semibold leading-tight tracking-tight text-white sm:text-6xl">
            Taghdisi Labs Digital —
            <span className="block text-cyan-400">Agency-grade product experiences</span>
          </h1>
          <p className="text-lg leading-8 text-slate-300 sm:text-xl">
            We build premium digital brands with polished interfaces, powerful storytelling, and conversion-driven design for the world’s top tech-forward companies.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row">
            <a
              href="#work"
              className="inline-flex items-center justify-center rounded-full bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Explore our work
            </a>
            <a
              href="#contact"
              className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
            >
              Start your project
            </a>
          </div>
        </div>

        <div className="mt-20 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {[
            {
              title: 'Product Strategy',
              description: 'From brand identity to digital growth systems, we help ambitious startups and scaleups launch with confidence.',
            },
            {
              title: 'Design & UI',
              description: 'Pixel-perfect interfaces with motion, clarity, and performance that elevate your product’s perception.',
            },
            {
              title: 'Web Development',
              description: 'Next.js 16 apps built for speed, SEO, and reliable delivery across desktop and mobile.',
            },
          ].map((item) => (
            <article key={item.title} className="rounded-4xl border border-white/10 bg-white/5 p-8 shadow-[0_20px_60px_rgba(15,23,42,0.35)] backdrop-blur-xl">
              <h2 className="text-xl font-semibold text-white">{item.title}</h2>
              <p className="mt-3 text-slate-300">{item.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="work" className="border-t border-white/10 bg-slate-900 px-6 py-20 lg:px-10">
        <div className="mx-auto max-w-6xl space-y-10">
          <div className="max-w-2xl">
            <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Featured capabilities</p>
            <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">Crafted for leading digital brands and modern SaaS teams.</h2>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="rounded-4xl bg-slate-950 p-8 ring-1 ring-white/10">
              <h3 className="text-xl font-semibold text-white">Design Systems</h3>
              <p className="mt-4 text-slate-400">Create scalable component libraries and visual systems that keep your product consistent across every experience.</p>
            </div>
            <div className="rounded-4xl bg-slate-950 p-8 ring-1 ring-white/10">
              <h3 className="text-xl font-semibold text-white">Conversion Growth</h3>
              <p className="mt-4 text-slate-400">Optimize user journeys, landing pages, and digital campaigns with measurable attention to performance and clarity.</p>
            </div>
            <div className="rounded-4xl bg-slate-950 p-8 ring-1 ring-white/10">
              <h3 className="text-xl font-semibold text-white">Technical Delivery</h3>
              <p className="mt-4 text-slate-400">Ship production-ready Next.js applications with modern deployment workflows and high availability.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="contact" className="px-6 py-20 lg:px-10">
        <div className="mx-auto max-w-4xl rounded-[3rem] bg-gradient-to-br from-cyan-500/10 via-slate-900 to-slate-950 p-10 ring-1 ring-white/10 backdrop-blur-2xl">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Ready to elevate?</p>
              <h2 className="mt-3 text-3xl font-semibold text-white sm:text-4xl">Let's build an exceptional digital experience.</h2>
            </div>
            <a
              href="mailto:hello@taghdisilabs.digital"
              className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-100"
            >
              Say hello
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}
