// League tier classification aligned with backend notebooks
// This provides comprehensive global league coverage

export type LeagueTier = 1 | 2 | 3

export interface LeagueInfo {
  code: string
  name: string
  tier: LeagueTier
  region: 'europe' | 'americas' | 'asia' | 'africa' | 'other'
}

// ============================================================
// TIER 1 - Top 5 European Leagues
// ============================================================
export const TIER_1_LEAGUES: LeagueInfo[] = [
  { code: 'ENG.1', name: 'Premier League', tier: 1, region: 'europe' },
  { code: 'ESP.1', name: 'La Liga', tier: 1, region: 'europe' },
  { code: 'ITA.1', name: 'Serie A', tier: 1, region: 'europe' },
  { code: 'GER.1', name: 'Bundesliga', tier: 1, region: 'europe' },
  { code: 'FRA.1', name: 'Ligue 1', tier: 1, region: 'europe' },
]

// ============================================================
// TIER 2 - European Secondary
// ============================================================
export const TIER_2_EUROPEAN: LeagueInfo[] = [
  // Second tier of major leagues
  { code: 'ENG.2', name: 'English Championship', tier: 2, region: 'europe' },
  { code: 'ENG.3', name: 'English League One', tier: 2, region: 'europe' },
  { code: 'ENG.4', name: 'English League Two', tier: 2, region: 'europe' },
  { code: 'ESP.2', name: 'La Liga 2', tier: 2, region: 'europe' },
  { code: 'ITA.2', name: 'Serie B', tier: 2, region: 'europe' },
  { code: 'GER.2', name: '2. Bundesliga', tier: 2, region: 'europe' },
  { code: 'FRA.2', name: 'Ligue 2', tier: 2, region: 'europe' },
  // Other top European first divisions
  { code: 'NED.1', name: 'Eredivisie', tier: 2, region: 'europe' },
  { code: 'POR.1', name: 'Primeira Liga', tier: 2, region: 'europe' },
  { code: 'BEL.1', name: 'Pro League', tier: 2, region: 'europe' },
  { code: 'TUR.1', name: 'Super Lig', tier: 2, region: 'europe' },
  { code: 'RUS.1', name: 'Premier Liga', tier: 2, region: 'europe' },
  { code: 'UKR.1', name: 'Premier League', tier: 2, region: 'europe' },
  { code: 'SCO.1', name: 'Scottish Premiership', tier: 2, region: 'europe' },
  { code: 'AUT.1', name: 'Bundesliga', tier: 2, region: 'europe' },
  { code: 'SUI.1', name: 'Super League', tier: 2, region: 'europe' },
  { code: 'GRE.1', name: 'Super League', tier: 2, region: 'europe' },
  { code: 'DEN.1', name: 'Superliga', tier: 2, region: 'europe' },
  { code: 'NOR.1', name: 'Eliteserien', tier: 2, region: 'europe' },
  { code: 'SWE.1', name: 'Allsvenskan', tier: 2, region: 'europe' },
  { code: 'POL.1', name: 'Ekstraklasa', tier: 2, region: 'europe' },
  { code: 'CZE.1', name: 'First League', tier: 2, region: 'europe' },
  { code: 'CRO.1', name: 'HNL', tier: 2, region: 'europe' },
  { code: 'SRB.1', name: 'SuperLiga', tier: 2, region: 'europe' },
  // European competitions
  { code: 'UEFA.CHAMPIONS', name: 'Champions League', tier: 2, region: 'europe' },
  { code: 'UEFA.EUROPA', name: 'Europa League', tier: 2, region: 'europe' },
  { code: 'UEFA.EUROPA.CONF', name: 'Conference League', tier: 2, region: 'europe' },
]

// ============================================================
// TIER 2 - Americas
// ============================================================
export const TIER_2_AMERICAS: LeagueInfo[] = [
  // North & Central America
  { code: 'USA.1', name: 'MLS', tier: 2, region: 'americas' },
  { code: 'MEX.1', name: 'Liga MX', tier: 2, region: 'americas' },
  { code: 'CAN.1', name: 'Canadian Premier League', tier: 2, region: 'americas' },
  { code: 'CONCACAF.CHAMPIONS', name: 'CONCACAF Champions League', tier: 2, region: 'americas' },
  // South America
  { code: 'BRA.1', name: 'Brasileirão Série A', tier: 2, region: 'americas' },
  { code: 'ARG.1', name: 'Liga Profesional', tier: 2, region: 'americas' },
  { code: 'COL.1', name: 'Liga BetPlay', tier: 2, region: 'americas' },
  { code: 'CHI.1', name: 'Primera División', tier: 2, region: 'americas' },
  { code: 'PER.1', name: 'Liga 1', tier: 2, region: 'americas' },
  { code: 'ECU.1', name: 'Serie A', tier: 2, region: 'americas' },
  { code: 'URU.1', name: 'Primera División', tier: 2, region: 'americas' },
  { code: 'CONMEBOL.LIBERTADORES', name: 'Copa Libertadores', tier: 2, region: 'americas' },
  { code: 'CONMEBOL.SUDAMERICANA', name: 'Copa Sudamericana', tier: 2, region: 'americas' },
]

// ============================================================
// TIER 2 - Asia & Oceania
// ============================================================
export const TIER_2_ASIA: LeagueInfo[] = [
  { code: 'JPN.1', name: 'J1 League', tier: 2, region: 'asia' },
  { code: 'KOR.1', name: 'K League 1', tier: 2, region: 'asia' },
  { code: 'CHN.1', name: 'Chinese Super League', tier: 2, region: 'asia' },
  { code: 'AUS.1', name: 'A-League', tier: 2, region: 'asia' },
  { code: 'SAU.1', name: 'Saudi Pro League', tier: 2, region: 'asia' },
  { code: 'UAE.1', name: 'UAE Pro League', tier: 2, region: 'asia' },
  { code: 'QAT.1', name: 'Qatar Stars League', tier: 2, region: 'asia' },
  { code: 'IND.1', name: 'Indian Super League', tier: 2, region: 'asia' },
  { code: 'AFC.CHAMPIONS', name: 'AFC Champions League', tier: 2, region: 'asia' },
]

// ============================================================
// TIER 2 - Africa
// ============================================================
export const TIER_2_AFRICA: LeagueInfo[] = [
  { code: 'RSA.1', name: 'Premier Soccer League', tier: 2, region: 'africa' },
  { code: 'EGY.1', name: 'Egyptian Premier League', tier: 2, region: 'africa' },
  { code: 'MAR.1', name: 'Botola Pro', tier: 2, region: 'africa' },
  { code: 'TUN.1', name: 'Ligue 1', tier: 2, region: 'africa' },
  { code: 'ALG.1', name: 'Ligue 1', tier: 2, region: 'africa' },
  { code: 'NGA.1', name: 'NPFL', tier: 2, region: 'africa' },
  { code: 'CAF.CHAMPIONS', name: 'CAF Champions League', tier: 2, region: 'africa' },
]

// All Tier 2 leagues combined
export const TIER_2_LEAGUES: LeagueInfo[] = [
  ...TIER_2_EUROPEAN,
  ...TIER_2_AMERICAS,
  ...TIER_2_ASIA,
  ...TIER_2_AFRICA,
]

// All classified leagues
export const ALL_LEAGUES: LeagueInfo[] = [
  ...TIER_1_LEAGUES,
  ...TIER_2_LEAGUES,
]

// Quick lookup by code
export const LEAGUE_MAP = new Map<string, LeagueInfo>(
  ALL_LEAGUES.map(league => [league.code, league]),
)

// Get tier for a league code
export function getLeagueTier(code: string): LeagueTier {
  return LEAGUE_MAP.get(code)?.tier ?? 3
}

// Get tier label
export function getTierLabel(tier: LeagueTier): string {
  switch (tier) {
    case 1:
      return 'Top 5'
    case 2:
      return 'Tier 2'
    case 3:
      return 'Other'
  }
}

// Get tier badge color classes
export function getTierBadgeClasses(tier: LeagueTier): string {
  switch (tier) {
    case 1:
      return 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30'
    case 2:
      return 'bg-gradient-to-r from-blue-500/20 to-cyan-500/20 text-blue-400 border-blue-500/30'
    case 3:
      return 'bg-white/5 text-muted-foreground border-white/10'
  }
}

// Region labels
export const REGION_LABELS: Record<LeagueInfo['region'], string> = {
  europe: '🇪🇺 Europe',
  americas: '🌎 Americas',
  asia: '🌏 Asia & Oceania',
  africa: '🌍 Africa',
  other: '🌐 Other',
}

// League tier stats summary
export const TIER_STATS = {
  tier1Count: TIER_1_LEAGUES.length,
  tier2Count: TIER_2_LEAGUES.length,
  totalClassified: ALL_LEAGUES.length,
  regions: {
    europe: [...TIER_1_LEAGUES, ...TIER_2_EUROPEAN].length,
    americas: TIER_2_AMERICAS.length,
    asia: TIER_2_ASIA.length,
    africa: TIER_2_AFRICA.length,
  },
}
