(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const header = document.querySelector('#site-header');
  window.addEventListener('scroll', () => header?.classList.toggle('scrolled', window.scrollY > 20), { passive: true });
  const scene = document.querySelector('#scene');
  if (scene && !reduced && window.matchMedia('(min-width: 901px)').matches) {
    const wrap = document.querySelector('.scene-wrap');
    wrap.addEventListener('pointermove', ({ clientX, clientY }) => { const box = wrap.getBoundingClientRect(), x = (clientX - box.left) / box.width - .5, y = (clientY - box.top) / box.height - .5; scene.style.transform = `translate(-50%,-50%) rotateX(${5 - y * 9}deg) rotateY(${-7 + x * 13}deg)`; });
    wrap.addEventListener('pointerleave', () => scene.style.transform = 'translate(-50%,-50%) rotateX(5deg) rotateY(-7deg)');
  }
  if (!window.gsap || reduced) return;
  gsap.registerPlugin(ScrollTrigger);
  gsap.from('.hero-copy > *', { y: 25, opacity: 0, stagger: .1, duration: .75, ease: 'power3.out' });
  gsap.from('.scene', { opacity: 0, scale: .84, x: 45, duration: 1.1, ease: 'power3.out', delay: .15 });
  gsap.utils.toArray('.section-intro, .flavour-copy, .operations-top, .order-flow > h2, .closing > div').forEach(el => gsap.from(el, { y: 35, opacity: 0, duration: .7, scrollTrigger: { trigger: el, start: 'top 84%' } }));
  gsap.utils.toArray('.capability-grid article, .feature-stack article, .food-card, .flow-line article').forEach((el, i) => gsap.from(el, { y: 28, opacity: 0, duration: .55, delay: i % 4 * .08, scrollTrigger: { trigger: el.parentElement, start: 'top 81%' } }));
  const count = document.querySelector('[data-count]');
  if (count) ScrollTrigger.create({ trigger: count, start: 'top 85%', once: true, onEnter: () => gsap.to({ value: 0 }, { value: Number(count.dataset.count), duration: 1.4, ease: 'power2.out', onUpdate() { count.textContent = Math.round(this.targets()[0].value); } }) });
})();
