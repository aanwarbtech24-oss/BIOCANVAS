/** Map protein category → Tailwind badge classes. */
export function categoryColor(cat: string): string {
  const map: Record<string, string> = {
    Transport:  'bg-sky-500/15 text-sky-400',
    Enzyme:     'bg-emerald-500/15 text-emerald-400',
    Hormone:    'bg-amber-500/15 text-amber-400',
    Storage:    'bg-violet-500/15 text-violet-400',
    Regulation: 'bg-rose-500/15 text-rose-400',
    Receptor:   'bg-cyan-500/15 text-cyan-400',
  }
  return map[cat] ?? 'bg-surface/60 text-muted-foreground'
}

/** Map ligand type → Tailwind badge classes. */
export function ligandTypeColor(type: string): string {
  const map: Record<string, string> = {
    Drug:             'bg-rose-500/15 text-rose-400',
    Cofactor:         'bg-amber-500/15 text-amber-400',
    Carbohydrate:     'bg-emerald-500/15 text-emerald-400',
    Stimulant:        'bg-orange-500/15 text-orange-400',
    Metabolite:       'bg-sky-500/15 text-sky-400',
    Antibiotic:       'bg-red-500/15 text-red-400',
    Neurotransmitter: 'bg-fuchsia-500/15 text-fuchsia-400',
    Lipid:            'bg-yellow-500/15 text-yellow-400',
  }
  return map[type] ?? 'bg-surface/60 text-muted-foreground'
}
