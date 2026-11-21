"""Rebuild figures from six preserved result streams, without rerunning MOA.

Run: python analysis/plot_six_runs.py
Requires matplotlib. Shading denotes sample SD across three learner seeds.
"""
import csv
import io
import statistics
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'figures'
OUT.mkdir(exist_ok=True)
FIELDS = {'accuracy': '[avg] classifications correct (percent)',
          'cpu': 'evaluation time (cpu seconds)'}
COLORS = {'moderate': '#1C5376', 'fast': '#AD4C24'}
streams = {}
with zipfile.ZipFile(ROOT / 'source/repeats-20261119-183637-313.zip') as z:
    for setting in ('moderate', 'fast'):
        for seed in (1, 2, 3):
            stem = f'full-{setting}-seed{seed}.csv'
            if seed == 1:
                text = (ROOT / 'source' / stem).read_text(encoding='utf-8-sig')
            else:
                raw = z.read(stem)
                text = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
            rows = list(csv.DictReader(io.StringIO(text)))
            assert len(rows) == 54
            streams[setting, seed] = rows

points = [int(float(r['learning evaluation instances'])) for r in streams['moderate', 1]]
assert points[-1] == 539383
stats = []
for setting in ('moderate', 'fast'):
    for i, n in enumerate(points):
        row = {'setting': setting, 'records': n, 'n_seeds': 3}
        for name, field in FIELDS.items():
            values = [float(streams[setting, seed][i][field]) for seed in (1, 2, 3)]
            row[name + '_mean'] = statistics.mean(values)
            row[name + '_sample_sd'] = statistics.stdev(values)
        stats.append(row)
with (ROOT / 'checkpoint_statistics.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(stats[0]))
    w.writeheader(); w.writerows(stats)

plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                     'axes.spines.top':False, 'axes.spines.right':False,
                     'axes.titleweight':'bold', 'axes.labelcolor':'#222222'})
fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.5), sharex=True, layout='constrained')
for ax, metric, ylabel, title in zip(axes, ('accuracy','cpu'),
        ('Cumulative accuracy (%)','Evaluation CPU time (seconds)'),
        ('A  Predictive performance','B  Computational cost')):
    for setting in ('moderate','fast'):
        subset = [r for r in stats if r['setting']==setting]
        x = [r['records']/1000 for r in subset]
        y = [r[metric+'_mean'] for r in subset]
        sd = [r[metric+'_sample_sd'] for r in subset]
        ax.plot(x,y,color=COLORS[setting],linewidth=1.7,label='ARF '+setting.title())
        ax.fill_between(x,[a-b for a,b in zip(y,sd)],[a+b for a,b in zip(y,sd)],
                        color=COLORS[setting],alpha=.18,linewidth=0)
    ax.set_ylabel(ylabel); ax.set_title(title,loc='left',fontsize=11)
    ax.grid(axis='y',alpha=.22); ax.set_xlim(0,540)
axes[0].legend(frameon=False,ncol=2,loc='lower left')
axes[1].set_xlabel('Processed records (thousands)')
fig.savefig(OUT / 'stream_progression.png',dpi=240)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7,3.6),layout='constrained')
for setting, offset in [('moderate',-.12),('fast',.12)]:
    values = [float(streams[setting,seed][-1][FIELDS['accuracy']]) for seed in (1,2,3)]
    ax.scatter([seed+offset for seed in (1,2,3)],values,color=COLORS[setting],s=55,
               label='ARF '+setting.title(),zorder=3)
    for seed,value in zip((1,2,3),values):
        ax.annotate(f'{value:.3f}',(seed+offset,value),xytext=(0,8 if setting=='fast' else -16),
                    textcoords='offset points',ha='center',fontsize=9)
ax.set_xticks([1,2,3]);ax.set_xlabel('Learner seed');ax.set_ylabel('Final cumulative accuracy (%)')
ax.set_ylim(63.48,63.85);ax.set_xlim(.5,3.5);ax.grid(axis='y',alpha=.22)
ax.legend(frameon=False,ncol=2,loc='upper center')
fig.savefig(OUT / 'seed_accuracy.png',dpi=240)
plt.close(fig)
print('Rebuilt checkpoint_statistics.csv and two figures from all six preserved runs.')
