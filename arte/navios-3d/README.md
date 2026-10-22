# Navios 3D (0 créditos)

Os seis navios do jogo foram modelados por código no Blender (`scripts/montar_navios.py`):

| Tipo | Descrição |
|---|---|
| `barcoPesca` | Barco de pesca com rede e cesto |
| `transporte` | Barco de transporte (coca) com castelo de popa e carga |
| `gale` | Galé com esporão de bronze, escudos azuis, vela latina e remos |
| `incendiario` | Incendiário com braseiro aceso e barris |
| `navioPesado` | Navio pesado com dois mastros, castelos e balista |
| `corsario` | Corsário de casco escuro com duas velas latinas e canhões |

- O casco fica só acima da linha de água, por isso os navios flutuam no jogo.
- As velas às riscas, o friso e as bandeiras são azuis e tomam a cor da equipa.
- Clips: Idle (balanço), Walk (balanço + remadas), Attack (recuo), Hit e Death (inclina e afunda, achatando para a água).

`scripts/navios.ts` gera os atlas de 8 direções e `scripts/integrar_navios.py` escreve `UNIT3D_NAVAL_DATA`.
No jogo, `drawShip3D` mantém a esteira, a sombra e o balanço do desenho antigo; o efeito `sink` usa os quadros de afundar.
