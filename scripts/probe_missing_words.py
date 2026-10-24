"""探针：一批常用词里，有哪些在六档 + 补充词典里**完全查不到**。

用途：给手写补充词典 `data/dict/extra.json` 提供**有依据**的种子清单 ——
不拍脑袋想词，而是先量出真实的缺口。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import wordlist  # noqa: E402

# 常用词 + 文学文本常见词（不是考试高频词，所以六档词表很可能没收）
WORDS = """
calico calicoes upholsterer unroll upstairs downstairs doorway doorway
chimney cupboard kettle towel soap basin pitcher tumbler
governor arena spectator prisoner guard executioner herald
trinket bauble ornament trinkets gewgaw curio
velvet satin linen calico gingham muslin damask
merchant peddler vendor wares bargain haggling
carnival pageant revelry masquerade
orchard meadow pasture thicket grove glade
staircase landing banister threshold
sermon parable proverb fable allegory
widow orphan heir legacy inheritance
tailor seamstress laundry ironing mending darning
physician apothecary remedy potion nostrum
carriage coachman axle rein harness
lantern candle candlestick wick
piano violin cello flute harp
novelist poet playwright essayist
typewriter inkwell blotter stationery
telegraph messenger postman courier
baker butcher grocer greengrocer
cobbler blacksmith milliner
nurse governess tutor schoolmaster
magistrate bailiff constable warden
cathedral abbey cloister chapel nave
banquet feast repast victuals Provisions
armor helmet shield lance banner
compass quadrant sextant
telescope microscope prism lens
almanac gazette pamphlet brochure
poster placard handbill broadside
suitcase satchel valise portmanteau
umbrella parasol galoshes
spectacles lorgnette monocle
pheasant partridge venison truffle
marmalade preserves pickles
mustard vinegar seasoning spice
porridge gruel broth stew
biscuit scone crumpet muffin
drawing-room parlour salon
pantry larder scullery
hearth fireside inglenook
garret attic cellar crypt
cobblestone pavement gutter kerb
lamppost milestone signpost
turnpike tollgate byway lane
brook rivulet cascade waterfall
cavern grotto ravine gully
prairie savanna tundra steppe
monsoon zephyr tempest gale
comet constellation galaxy nebula
eclipse solstice equinox
harvest sow reap thresh
orchard vineyard brewery
weaver spinner dyer loom
quill parchment vellum scroll
ledger invoice receipt debit
mortgage tenancy lease deed
notary witness testimony oath
verdict acquittal pardon reprieve
dungeon gibbet pillory
procession cortege funeral bier
elegy epitaph obituary
nuptial bridal dowry
cradle crib rattle
schoolroom chalk slate abacus
alphabet primer copybook
riddle conundrum enigma
lullaby nursery rhyme
harvest home yule easter
carnival lent advent
pilgrim crusade shrine relic
monastery convent hermitage
almsgiving tithe offering
oracle prophet sibyl augur
labyrinth minotaur centaur
sphinx griffin phoenix unicorn
parliament senate caucus veto
republic monarchy oligarchy
patriot traitor desereter
frontier colony settlement outpost
caravan convoy expedition
anchor mooring buoy rudder
mast sail rigging yardarm
galley frigate schooner clipper
compass astrolabe
sawmill grindstone anvil
bellows forge crucible
tinder flint ember ash
cauldron vat tun cask
brewery distillery vineyard
harrows plough scythe flail
granary silo threshing
pastoral idyll bucolic
serene placid tranquil
melancholy wistful pensive
brisk nimble deft adroit
clumsy awkward gauche
frugal thrifty provident
lavish prodigal munificent
haughty supercilious disdainful
meek humble unassuming
obstinate stubborn headstrong
docile tractable amenable
astute shrewd discerning
ingenuous artless guileless
candid frank forthright
taciturn laconic succinct
verbose prolix rambling
lucid perspicuous eloquent
arcane esoteric abstruse
quaint droll whimsical
dilapidated ramshackle decrepit
pristine immaculate spotless
squalid foul noisome
balmy salubrious wholesome
inclement stormy tempestuous
arid parched barren
fertile fecund prolific
luxuriant rank overgrown
verdant leafy foliated
sombre gloomy murky
radiant resplendent dazzling
pallid ashen sallow
florid ruddy rubicund
comely fair beauteous
homely plain unlovely
grotesque hideous repulsive
elegant graceful exquisite
clumsy lumbering ponderous
sprightly vivacious buoyant
languid listless lethargic
indolent slothful shiftless
diligent industrious sedulous
assiduous persevering tenacious
obdurate unyielding adamant
compliant acquiescent deferential
imperious domineering overbearing
solicitous attentive considerate
oblivious unmindful heedless
cognizant aware apprised
privy informed apprised
""".split()

out: list[str] = []
gaps: list[str] = []
have: list[str] = []
idx = wordlist._index()
gen = wordlist._general()

for w in sorted(set(WORDS)):
    _lm, mask = wordlist.lookup(w)
    if mask:
        have.append(w)
        continue
    if wordlist.lookup_entry(w, "cet6"):
        have.append(w)
        continue
    gaps.append(w)

out.append(f"测试 {len(set(WORDS))} 个常用词：有词条 {len(have)} 个，**完全查不到 {len(gaps)} 个**")
out.append("")
out.append("完全查不到的词（按字母序）：")
for i in range(0, len(gaps), 6):
    out.append("  " + "  ".join(gaps[i:i + 6]))

print("\n".join(out))
