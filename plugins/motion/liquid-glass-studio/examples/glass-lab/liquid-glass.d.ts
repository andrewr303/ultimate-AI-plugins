// Liquid Glass Studio engine: liquid glass style refraction for the web.
// Type declarations for liquid-glass.js. MIT License (see the plugin LICENSE).
// Not affiliated with Apple. "Liquid Glass" is Apple's name for its material.
//
// To use the engine in a TypeScript project, copy liquid-glass.js and this
// file side by side, and keep this header and the one in liquid-glass.js.
// tests/docs_drift.test.mjs fails if the exports here and in liquid-glass.js
// differ, or if GlassOptions and DEFAULTS name different options.

/* Pure math ---------------------------------------------------------------- */

export type ProfileFunction = (t: number) => number;
export type ProfileName = 'convexCircle' | 'convexSquircle' | 'concave' | 'lip';
export type Profile = ProfileName | ProfileFunction;
export type Shape = 'rounded' | 'squircle';
export type Tier = 'refract' | 'frost' | 'solid';
export type Engine = 'chromium' | 'webkit' | 'gecko' | 'unknown';

export declare function smoothstep(e0: number, e1: number, x: number): number;
export declare function smootherstep(t: number): number;

export declare function convexCircle(t: number): number;
export declare function convexSquircle(t: number): number;
export declare function concave(t: number): number;
export declare function lip(t: number): number;
export declare const PROFILES: Readonly<Record<ProfileName, ProfileFunction>>;

export interface RefractionProfileOptions {
  bezelWidth?: number;
  thickness?: number;
  ior?: number;
  profile?: Profile;
  samples?: number;
  strength?: number;
}
/** Signed offsets in px across the bezel; positive samples inward. */
export declare function refractionProfile(options?: RefractionProfileOptions): Float64Array;

export declare function roundedRectSDF(x: number, y: number, hw: number, hh: number, r: number, shape?: Shape): number;

export declare const NEUTRAL: 128;
export declare const NEUTRAL_BIAS: number;
export declare function encodeDisplacement(offset: number, maxDisplacement: number): number;
export declare function decodeDisplacement(byte: number, maxDisplacement: number, filterScale?: number): number;

export interface DisplacementFieldOptions {
  /** CSS px */
  width: number;
  /** CSS px */
  height: number;
  radius?: number;
  bezelWidth?: number;
  profile?: Profile;
  ior?: number;
  thickness?: number;
  scale?: number;
  strength?: number;
  /** Map pixels per CSS px. */
  pixelRatio?: number;
  shape?: Shape;
  foldHeadroom?: number;
  minJacobian?: number;
}
export interface DisplacementField {
  /** Map pixels (CSS px times pixelRatio). */
  width: number;
  /** Map pixels (CSS px times pixelRatio). */
  height: number;
  cssWidth: number;
  cssHeight: number;
  pixelRatio: number;
  data: Uint8ClampedArray;
  neutral: number;
  neutralBias: number;
  maxDisplacement: number;
  filterScale: number;
  /** Fold guard amplitude factor, 0 to 1. */
  attenuation: number;
  minJacobian: number;
  bezelWidth: number;
  radius: number;
  fieldRadius: number;
  /** Width in CSS px of the fade to neutral at the outer edge. */
  fadeBand: number;
}
export declare function displacementField(options: DisplacementFieldOptions): DisplacementField;

export interface SpecularFieldOptions {
  width: number;
  height: number;
  radius?: number;
  shape?: Shape;
  pixelRatio?: number;
  lightAngle?: number;
  intensity?: number;
  rimWidth?: number;
}
export interface SpecularField {
  width: number;
  height: number;
  cssWidth: number;
  cssHeight: number;
  pixelRatio: number;
  data: Uint8ClampedArray;
}
export declare function specularField(options: SpecularFieldOptions): SpecularField;

export interface FilterMarkupOptions {
  id: string;
  mapHref: string;
  specularHref?: string;
  width: number;
  height: number;
  scale: number;
  chromaticAberration?: number;
  blur?: number;
  saturation?: number;
  neutralBias?: number;
  specularOpacity?: number;
}
export declare function buildFilterMarkup(options: FilterMarkupOptions): string;

export interface TierInput {
  reducedTransparency?: boolean;
  contrastMore?: boolean;
  forcedColors?: boolean;
  solidSurfaces?: boolean;
  supportsBackdrop?: boolean;
  engine?: Engine | string;
  preferred?: Tier | 'auto';
}
export interface TierDecision {
  tier: Tier;
  reason: string;
}
export declare function explainTier(input?: TierInput): TierDecision;
export declare function detectTier(input?: TierInput): Tier;

export interface NavigatorLike {
  userAgent?: string;
  vendor?: string;
  userAgentData?: { brands?: Array<{ brand: string; version?: string }> };
}
export declare function detectEngine(nav: NavigatorLike | null | undefined): Engine;

/* Browser API ---------------------------------------------------------------- */

export declare const SOLID_SURFACES_ATTRIBUTE: 'data-glass-surfaces';
export declare const MEDIA_QUERIES: Readonly<{
  reducedTransparency: string;
  contrastMore: string;
  forcedColors: string;
  reducedMotion: string;
}>;

export interface Capabilities {
  reducedTransparency: boolean;
  contrastMore: boolean;
  forcedColors: boolean;
  reducedMotion: boolean;
  /** True while <html data-glass-surfaces="solid"> is set. */
  solidSurfaces: boolean;
  supportsBackdrop: boolean;
  engine: Engine;
}
export declare function capabilities(win?: Window | null): Capabilities;

export declare function findBackdropRoot(element: Element): { element: Element; property: string } | null;

export interface GlassInfo {
  tier: Tier;
  reason: string;
  engine: Engine;
  /** CSS px */
  width: number;
  /** CSS px */
  height: number;
  pixelRatio: number;
  // Present in the refract tier only:
  /** Map pixels (width times pixelRatio). */
  mapWidth?: number;
  /** Map pixels (height times pixelRatio). */
  mapHeight?: number;
  radius?: number;
  filterId?: string;
  cacheHit?: boolean;
  buildMs?: number;
  mapUrl?: string;
  specularUrl?: string;
  neutral?: number;
  neutralBias?: number;
  maxDisplacement?: number;
  filterScale?: number;
  attenuation?: number;
  minJacobian?: number;
  bezelWidth?: number;
  fieldRadius?: number;
  fadeBand?: number;
}

export interface GlassOptions {
  tier?: Tier | 'auto';
  radius?: number | 'auto';
  bezelWidth?: number;
  thickness?: number;
  ior?: number;
  profile?: Profile;
  shape?: Shape;
  strength?: number;
  chromaticAberration?: number;
  blur?: number;
  saturation?: number;
  frostBlur?: number;
  specularIntensity?: number;
  lightAngle?: number;
  rimWidth?: number;
  elasticity?: number;
  foldGuard?: boolean;
  maxPixelRatio?: number;
  warn?: boolean;
  onRender?: ((info: GlassInfo) => void) | null;
}
export declare const DEFAULTS: Readonly<Required<GlassOptions>>;

export declare const BASE_STYLES_ID: 'lgs-base-styles';
export declare const BASE_STYLES: string;

export interface GlassHandle {
  readonly element: HTMLElement;
  /** null until the first render finishes. */
  readonly tier: Tier | null;
  readonly info: GlassInfo | Record<string, never>;
  update(options?: GlassOptions): void;
  refresh(): void;
  destroy(): void;
}
export declare function createGlass(element: HTMLElement, options?: GlassOptions): GlassHandle;

export declare function clearGlassCache(): void;
