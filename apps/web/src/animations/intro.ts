import { gsap } from 'gsap'

export function animateIntro(selector: string) {
  const timeline = gsap.timeline()
  timeline.from(selector, { opacity: 0, y: 24, duration: 0.8, ease: 'power3.out' })
  return timeline
}
