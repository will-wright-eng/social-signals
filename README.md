# SOSIG (Social Signal) Command Line Tool

A command-line tool for analyzing GitHub repositories and calculating social signals based on various metrics.

## Features

- Analyze local Git repositories for various metrics and social signals
- Store and manage repository analysis data in a local database
- Configure analysis weights and parameters
- View repository statistics and comparisons
- Database management and optimization utilities

## Installation

```bash
# Clone the repository
git clone https://github.com/will-wright-eng/social-signals.git
cd social-signals/sosig/

# Install dependencies (rye is the perferred project manager)
rye sync

# or, using pip
pip install -r requirements.lock

# for development
pip install -r requirements-dev.lock
```

### Requirements

The CLI was setup on my macbook pro so the current support is exclusive to MacOS with the following command line tools:

- `git`
- `gh`

## Usage

SOSIG provides three main command groups:

### GitHub Metrics Operations (`gh`)

```bash
# Analyze repositories
sosig gh analyze path/to/repo1 path/to/repo2

# List analyzed repositories
sosig gh list
```

alternatively, you can use the bash scripts to analyze repos from a specific user

```bash
# generate public_repo_urls.txt file
make user-repos user=will-wright-eng

# analyze each repo in list
make analyze-repos user=will-wright-eng
```

you can create a custom list to analyze using the following steps

```bash
mkdir scripts/results/tf
cat << EOF >> scripts/results/tf/public_repo_urls.txt
github.com/gruntwork-io/terragrunt
github.com/cycloidio/terracognita
github.com/gruntwork-io/terratest
github.com/open-policy-agent/opa
github.com/bridgecrewio/checkov
github.com/terraform-compliance/cli
github.com/hashicorp/terraform
github.com/aquasecurity/tfsec
github.com/terraform-linters/tflint
github.com/tenable/terrascan
github.com/env0/terratag
github.com/minamijoyo/tfmigrate
github.com/opentofu/opentofu
github.com/dineshba/tf-summarize
EOF

# analyze custom list of open source repos
make analyze-repos user=tf
```

### Database Operations (`db`)

```bash
# View database statistics
sosig db stats

# Show database schema
sosig db schema

# Remove specific repository
sosig db remove repo-name

# Optimize database
sosig db vacuum
```

### Configuration Operations (`config`)

```bash
# Show current configuration
sosig config show
```

## Project Structure

```
sosig/
├── src/sosig/
│   ├── commands/          # CLI command implementations
│   ├── core/             # Core functionality and models
│   └── utils/            # Utility functions and services
├── scripts/              # Helper scripts
│   └── results/          # Analysis results
└── requirements.lock     # Locked dependencies
```

## Scripts

The project includes several utility scripts:

- `analyze-repo-file.sh`: Batch analyze repositories from a file
- `fetch-repos.sh`: Fetch repository information from GitHub

## Development

### Setup

```bash
rye add pip
rye sync
rye build
python -m pip install -e .
```

### Debug Mode

All commands support a `--debug` flag for additional logging:

```bash
sosig gh analyze path/to/repo --debug
```

### Workspace Configuration

Analysis operations use a workspace directory (default: `~/.local/share/ssig/workspace`):

```bash
sosig gh analyze path/to/repo --workspace /custom/path
```

## Examples

### Hugo Themes

| name                           | update_frequency_days | stars | social_signal | lines_of_code | age_days | username             | contributor_count | commit_count | open_issues |
|--------------------------------|-----------------------|-------|---------------|---------------|----------|----------------------|-------------------|--------------|-------------|
| hugo-blox-builder              | 1.7                   | 8440  | 81.6          | 284803        | 3205     | HugoBlox             | 204               | 1866         | 19          |
| docsy                          | 1.2                   | 2681  | 81.4          | 30171         | 2345     | google               | 186               | 1910         | 211         |
| hugo-PaperMod                  | 2.3                   | 10848 | 78.6          | 6482          | 2583     | adityatelange        | 256               | 1118         | 42          |
| FixIt                          | 1.1                   | 903   | 78.4          | 59120         | 2193     | hugo-fixit           | 68                | 1943         | 23          |
| hugo-theme-hello-4s3ti         | 4.2                   | 1481  | 76.2          | 406381        | 2390     | rhazdon              | 126               | 508          | 57          |
| congo                          | 0.7                   | 1331  | 75.7          | 76224         | 1273     | jpanther             | 144               | 1705         | 10          |
| blowfish                       | 0.3                   | 1702  | 75.6          | 282714        | 878      | nunocoracao          | 198               | 2820         | 82          |
| toha                           | 2.6                   | 1079  | 74.7          | 38152         | 1760     | hugo-toha            | 114               | 665          | 44          |
| hugo-theme-hello-friend-ng     | 3.7                   | 1071  | 73.8          | 39753         | 2390     | panr                 | 187               | 622          | 22          |
| beautifulhugo                  | 5.2                   | 1165  | 73.4          | 55525         | 3255     | halogenica           | 132               | 616          | 102         |
| hugo-theme-stack               | 2.5                   | 5317  | 72.9          | 11780         | 1627     | CaiJimmy             | 126               | 640          | 12          |
| hugo-paper                     | 4.3                   | 2180  | 72.4          | 10432         | 2583     | nanxiaobei           | 59                | 584          | 2           |
| hugo-theme-relearn             | 1.2                   | 470   | 72.2          | 89054         | 3246     | McShelby             | 127               | 2744         | 20          |
| hugo-book                      | 4.6                   | 3585  | 71.5          | 16820         | 2344     | alex-shpak           | 85                | 505          | 16          |
| hugo-clarity                   | 1.9                   | 597   | 71.5          | 25944         | 1754     | chipzoller           | 70                | 907          | 36          |
| gohugo-theme-ananke            | 5.8                   | 1216  | 71.1          | 28419         | 2856     | theNewDynamic        | 119               | 490          | 73          |
| hugo-theme-bootstrap           | 0.7                   | 526   | 70.8          | 60295         | 1570     | razonyang            | 57                | 2240         | 3           |
| hugo-coder                     | 5.7                   | 2799  | 70.8          | 47115         | 2532     | luizdepra            | 183               | 444          | 68          |
| doks                           | 1.8                   | 2167  | 70.0          | 15272         | 1756     | thuliteio            | 24                | 937          | 36          |
| anatole                        | 2.4                   | 673   | 70.0          | 25587         | 1760     | lxndrblz             | 87                | 710          | 14          |
| Mainroad                       | 6.5                   | 950   | 68.6          | 14466         | 2973     | Vimux                | 55                | 436          | 21          |
| hugo-geekdoc                   | 1.8                   | 519   | 67.6          | 46353         | 1850     | thegeeklab           | 36                | 1024         | 9           |
| FeelIt                         | 1.9                   | 167   | 67.0          | 112120        | 2193     | khusika              | 56                | 965          | 27          |
| hugo-theme-introduction        | 6.5                   | 678   | 66.8          | 256948        | 2885     | victoriadrake        | 59                | 445          | 4           |
| bilberry-hugo-theme            | 3.6                   | 362   | 66.0          | 131268        | 2657     | Lednerb              | 61                | 727          | 2           |
| hugo-profile                   | 3.6                   | 818   | 64.1          | 20294         | 1633     | gurusabarish         | 38                | 445          | 35          |
| jughead                        | 8.9                   | 1091  | 62.6          | 279702        | 1762     | athul                | 35                | 199          | 21          |
| hextra                         | 1.6                   | 949   | 61.8          | 35276         | 565      | imfing               | 63                | 340          | 57          |
| hugo-universal-theme           | 12.0                  | 828   | 61.3          | 90511         | 3157     | devcows              | 72                | 255          | 41          |
| hugo-notepadium                | 2.4                   | 333   | 60.0          | 31668         | 1899     | cntrump              | 29                | 784          | 14          |
| hugo-theme-jane                | 5.2                   | 941   | 59.7          | 328250        | 138      | xianmin              | 62                | 496          | 61          |
| hugo-theme-mini                | 10.3                  | 757   | 59.5          | 3332          | 2938     | nodejh               | 46                | 254          | 38          |
| hugo-theme-terminal            | 6.6                   | 2198  | 59.1          | 16559         | 959      | panr                 | 154               | 144          | 9           |
| hugo-theme-dream               | 4.7                   | 418   | 58.6          | 22917         | 2678     | g1eny0ung            | 34                | 573          | 6           |
| compose                        | 2.8                   | 320   | 58.1          | 30740         | 1831     | onweru               | 28                | 661          | 24          |
| reveal-hugo                    | 6.8                   | 702   | 57.4          | 51546         | 2475     | joshed-io            | 27                | 352          | 35          |
| hugo-theme-anubis2             | 3.4                   | 71    | 57.1          | 6189          | 1850     | Junyi-99             | 45                | 523          | 6           |
| hugo-theme-diary               | 7.3                   | 597   | 56.6          | 25947         | 1912     | AmazingRise          | 36                | 256          | 11          |
| github-style                   | 8.0                   | 606   | 56.3          | 8714          | 1933     | MeiK2333             | 37                | 240          | 29          |
| hugo-theme-zen                 | 4.0                   | 294   | 56.1          | 10336         | 2889     | frjo                 | 26                | 714          | 1           |
| hugo-theme-cleanwhite          | 11.2                  | 741   | 55.6          | 50701         | 2424     | zhaohuabing          | 37                | 213          | 9           |
| triple-hyde                    | 9.6                   | 253   | 55.4          | 32343         | 3936     | htr3n                | 67                | 412          | 13          |
| hugo-blog-awesome              | 2.4                   | 527   | 54.9          | 16349         | 721      | hugo-sid             | 51                | 283          | 4           |
| hugo-theme-iris                | 0.9                   | 72    | 53.8          | 31348         | 2019     | peaceiris            | 9                 | 2259         | 42          |
| castanet                       | 5.2                   | 118   | 53.8          | 171002        | 3057     | mattstratton         | 29                | 560          | 32          |
| hinode                         | 0.3                   | 167   | 53.7          | 125776        | 1119     | gethinode            | 19                | 4335         | 22          |
| gokarna-hugo                   | 4.5                   | 424   | 52.9          | 34231         | 1354     | gokarna-theme        | 36                | 298          | 10          |
| hugo-bearcub                   | 8.8                   | 941   | 52.9          | 3404          | 1614     | janraasch            | 20                | 182          | 4           |
| hermit-V2                      | 8.1                   | 117   | 52.9          | 3682          | 2296     | 1bl4z3r              | 50                | 283          | 2           |
| hugo-scroll                    | 6.1                   | 289   | 52.6          | 43916         | 1672     | zjedi                | 38                | 261          | 10          |
| KeepIt                         | 11.4                  | 298   | 51.7          | 1000582       | 2193     | Fastbyte01           | 16                | 188          | 1           |
| hugoplate                      | 2.8                   | 1031  | 51.4          | 25379         | 621      | zeon-studio          | 20                | 220          | 11          |
| hugo-theme-w3css-basic         | 2.6                   | 67    | 51.2          | 188678        | 2645     | it-gro               | 3                 | 958          | 7           |
| hugo-theme-gruvbox             | 1.1                   | 214   | 51.2          | 54974         | 1334     | schnerring           | 7                 | 1162         | 28          |
| adritian-free-hugo-theme       | 4.0                   | 122   | 50.2          | 103397        | 1869     | zetxek               | 20                | 464          | 2           |
| hugo-theme-cactus              | 7.9                   | 553   | 49.7          | 49262         | 1669     | monkeyWzr            | 23                | 170          | 25          |
| paige                          | 0.4                   | 254   | 49.4          | 217866        | 880      | willfaught           | 5                 | 1728         | 6           |
| hugo-geekblog                  | 2.1                   | 100   | 48.8          | 44702         | 1682     | thegeeklab           | 5                 | 821          | 3           |
| hugo_theme_pickles             | 10.8                  | 223   | 48.5          | 21357         | 3315     | mismith0227          | 36                | 300          | 17          |
| hugo-fresh                     | 12.7                  | 650   | 48.4          | 6771          | 2376     | StefMa               | 24                | 179          | 23          |
| poison                         | 2.1                   | 260   | 48.2          | 69707         | 823      | lukeorth             | 34                | 317          | 27          |
| archie                         | 22.0                  | 1091  | 47.2          | 15142         | 1762     | athul                | 33                | 81           | 21          |
| perplex                        | 0.9                   | 30    | 46.6          | 289646        | 1004     | bowman2001           | 5                 | 910          | 15          |
| hugo-vitae                     | 7.9                   | 143   | 46.0          | 35268         | 1875     | dataCobra            | 26                | 223          | 10          |
| alpha-church                   | 5.3                   | 69    | 45.4          | 48267         | 2472     | funkydan2            | 13                | 439          | 5           |
| osprey-delight                 | 8.6                   | 106   | 44.9          | 20349         | 2822     | kdevo                | 23                | 333          | 1           |
| lotusdocs                      | 1.8                   | 407   | 44.6          | 55651         | 834      | colinwilson          | 9                 | 473          | 8           |
| hugo-theme-monochrome          | 3.6                   | 193   | 44.4          | 19553         | 1462     | kaiiiz               | 11                | 391          | 7           |
| tailbliss                      | 2.2                   | 340   | 44.4          | 101088        | 829      | nusserstudios        | 16                | 343          | 4           |
| hugo-kiera                     | 10.5                  | 94    | 43.8          | 17342         | 2647     | avianto              | 28                | 241          | 11          |
| Binario                        | 7.3                   | 117   | 43.6          | 12099         | 2551     | Vimux                | 15                | 328          | 8           |
| risotto                        | 9.4                   | 469   | 43.3          | 3325          | 1432     | joeroe               | 19                | 143          | 15          |
| docuapi                        | 17.7                  | 757   | 43.3          | 6805          | 3031     | bep                  | 16                | 169          | 15          |
| hugo-theme-gallery             | 1.4                   | 424   | 43.3          | 13529         | 572      | nicokaiser           | 14                | 399          | 9           |
| hugo-theme-nix                 | 14.7                  | 136   | 43.0          | 3934          | 3053     | lordmathis           | 37                | 205          | 1           |
| hugo-classic                   | 21.4                  | 787   | 42.9          | 12221         | 2790     | yihui                | 25                | 123          | 15          |
| Blonde                         | 4.9                   | 115   | 42.9          | 6260          | 1634     | opera7133            | 11                | 336          | 4           |
| newsroom                       | 10.2                  | 299   | 42.4          | 17495         | 1999     | onweru               | 14                | 196          | 3           |
| hugo-theme-techdoc             | 8.8                   | 220   | 42.3          | 60717         | 2529     | thingsym             | 9                 | 289          | 14          |
| hugo-flex                      | 6.4                   | 107   | 42.3          | 1629          | 2178     | ldeso                | 9                 | 331          | 0           |
| lynx                           | 4.4                   | 390   | 42.1          | 6455          | 1191     | jpanther             | 10                | 209          | 0           |
| slick                          | 7.5                   | 56    | 42.0          | 120741        | 2612     | spookey              | 9                 | 350          | 0           |
| hugo-refresh                   | 8.6                   | 117   | 41.9          | 206198        | 2044     | PippoRJ              | 10                | 217          | 3           |
| gohugo-theme-ed                | 1.4                   | 68    | 41.7          | 16812         | 1046     | sergeyklay           | 2                 | 746          | 0           |
| hugo-theme-virgo               | 1.8                   | 111   | 41.3          | 227411        | 959      | loveminimal          | 2                 | 535          | 0           |
| bridget                        | 1.2                   | 122   | 41.2          | 232480        | 698      | Sped0n               | 5                 | 577          | 4           |
| typo                           | 1.5                   | 318   | 40.9          | 25617         | 288      | tomfran              | 26                | 189          | 9           |
| tella                          | 6.6                   | 120   | 40.6          | 45514         | 1493     | opera7133            | 14                | 226          | 11          |
| henry-hugo                     | 2.8                   | 63    | 40.3          | 6884          | 1305     | kaushikgopal         | 4                 | 464          | 3           |
| hugo-product-launch            | 6.8                   | 67    | 39.6          | 215517        | 1611     | janraasch            | 5                 | 237          | 1           |
| shadocs                        | 3.7                   | 52    | 39.5          | 48549         | 1223     | jgazeau              | 11                | 289          | 7           |
| hugo-goa                       | 22.8                  | 265   | 39.4          | 26890         | 3041     | shenoydotme          | 43                | 129          | 0           |
| simpleit-hugo-theme            | 6.4                   | 16    | 39.3          | 79217         | 2373     | marcanuy             | 2                 | 299          | 0           |
| soho                           | 26.7                  | 574   | 38.9          | 2951          | 3936     | spf13                | 37                | 135          | 8           |
| lightbi-hugo                   | 8.3                   | 104   | 38.8          | 112230        | 1598     | binokochumolvarghese | 10                | 184          | 5           |
| capsule                        | 7.8                   | 23    | 38.6          | 19306         | 2900     | sudorook             | 3                 | 369          | 0           |
| hugo-theme-re-terminal         | 5.7                   | 74    | 38.3          | 16733         | 959      | mirus-ua             | 24                | 166          | 5           |
| hugo-bearblog                  | 21.8                  | 941   | 37.4          | 1743          | 1614     | janraasch            | 8                 | 74           | 4           |
| qubt                           | 0.9                   | 77    | 37.3          | 163671        | 437      | chrede88             | 5                 | 514          | 1           |
| hugo-theme-yinyang             | 17.1                  | 496   | 37.2          | 2671          | 2279     | joway                | 9                 | 128          | 4           |
| devfest-theme-hugo             | 13.4                  | 90    | 37.1          | 27467         | 2216     | GDGToulouse          | 17                | 148          | 7           |
| L1nkr                          | 0.9                   | 27    | 36.6          | 22303         | 482      | chrede88             | 7                 | 565          | 1           |
| hugo-dead-simple               | 2.7                   | 71    | 36.5          | 5327          | 1021     | barklan              | 2                 | 366          | 0           |
| hugo-resume                    | 18.5                  | 280   | 35.8          | 23325         | 2548     | eddiewebb            | 18                | 137          | 5           |
| ink-free                       | 15.0                  | 41    | 35.6          | 9061          | 2127     | chollinger93         | 20                | 140          | 2           |
| plague                         | 2.9                   | 4     | 35.6          | 2984          | 1157     | brianreumere         | 1                 | 304          | 1           |
| Lowkey-Hugo-Theme              | 6.2                   | 168   | 35.3          | 12765         | 766      | nixentric            | 18                | 113          | 7           |
| hugo-bootstrap-theme           | 4.0                   | 108   | 34.9          | 45280         | 996      | filipecarneiro       | 2                 | 236          | 0           |
| hyde                           | 40.5                  | 574   | 34.9          | 2920          | 3936     | spf13                | 34                | 95           | 8           |
| dark-theme-editor              | 4.6                   | 35    | 34.8          | 6048          | 1087     | JingWangTW           | 6                 | 234          | 0           |
| hugo-theme-notrack             | 11.4                  | 47    | 34.7          | 102047        | 1725     | gevhaz               | 6                 | 151          | 8           |
| bootstrap-bp-hugo-theme        | 14.6                  | 54    | 34.2          | 96039         | 2291     | spech66              | 10                | 154          | 0           |
| kaslaanka                      | 12.5                  | 20    | 33.7          | 4530          | 2597     | iossefy              | 6                 | 200          | 1           |
| autophugo                      | 19.4                  | 98    | 33.7          | 140566        | 3027     | kc0bfv               | 18                | 153          | 7           |
| devise                         | 19.1                  | 111   | 33.7          | 385762        | 2055     | austingebauer        | 10                | 104          | 1           |
| seven                          | 1.6                   | 51    | 33.6          | 19482         | 600      | mrhelloboy           | 2                 | 344          | 0           |
| hugo-theme-moments             | 8.6                   | 146   | 33.4          | 9442          | 1279     | FarseaSH             | 4                 | 142          | 16          |
| hugo-theme-tailwind            | 3.3                   | 130   | 33.4          | 24348         | 475      | tomowang             | 12                | 139          | 1           |
| hugo-theme-tokiwa              | 17.1                  | 110   | 33.3          | 353012        | 1773     | heyeshuang           | 6                 | 101          | 2           |
| hugo-texify3                   | 2.6                   | 28    | 33.1          | 69161         | 598      | weastur              | 7                 | 217          | 2           |
| hugo-xterm                     | 7.5                   | 42    | 32.7          | 11506         | 1342     | manid2               | 2                 | 152          | 1           |
| aafu                           | 12.8                  | 55    | 32.5          | 5075          | 2157     | darshanbaral         | 2                 | 167          | 1           |
| theme-start                    | 1.8                   | 26    | 32.3          | 15571         | 508      | hbstack              | 4                 | 279          | 5           |
| photophobia                    | 7.9                   | 27    | 32.0          | 3908          | 1294     | setsevireon          | 4                 | 130          | 3           |
| salinger-theme                 | 2.2                   | 35    | 32.0          | 8994          | 709      | jacksalici           | 2                 | 181          | 1           |
| vnovel                         | 9.4                   | 21    | 32.0          | 3751          | 1395     | opera7133            | 5                 | 149          | 0           |
| digital-garden-hugo-theme      | 13.5                  | 265   | 31.7          | 4107          | 1145     | apvarun              | 12                | 82           | 10          |
| hugo-xmin                      | 33.9                  | 787   | 31.4          | 827           | 2790     | yihui                | 12                | 83           | 15          |
| hugo-theme-itheme              | 3.7                   | 70    | 31.3          | 14271         | 701      | floyd-li             | 5                 | 85           | 9           |
| hugo-theme-nightfall           | 6.9                   | 96    | 31.2          | 9352          | 727      | lordmathis           | 11                | 107          | 1           |
| hugo-creator                   | 7.3                   | 7     | 31.0          | 16931         | 1103     | CloudWithChris       | 4                 | 153          | 2           |
| hugo-JuiceBar                  | 6.8                   | 29    | 31.0          | 4608          | 1031     | hotjuicew            | 4                 | 148          | 4           |
| Niello                         | 15.6                  | 43    | 31.0          | 42031         | 2224     | guangmean            | 5                 | 143          | 0           |
| hugo-theme-spaced-blog         | 4.0                   | 5     | 30.7          | 40941         | 735      | Morgscode            | 3                 | 158          | 0           |
| dot-org-hugo-theme             | 3.7                   | 48    | 30.5          | 24511         | 592      | cncf                 | 4                 | 149          | 5           |
| hugo-theme-event               | 0.7                   | 6     | 30.3          | 23200         | 189      | medialesson          | 5                 | 247          | 5           |
| NewBee                         | 0.0                   | 50    | 30.2          | 47186         | 436      | xioyito              | 1                 | 1            | 4           |
| hugo-split-theme               | 19.5                  | 18    | 30.1          | 23714         | 2603     | christianmendoza     | 15                | 130          | 4           |
| hugo-theme-walden              | 5.6                   | 12    | 30.0          | 59379         | 797      | Homecat805           | 4                 | 112          | 1           |
| tophat-theme                   | 1.2                   | 10    | 29.9          | 3530          | 560      | sergiobarriel        | 1                 | 84           | 1           |
| colordrop                      | 16.0                  | 22    | 29.8          | 16856         | 2022     | humrochagf           | 5                 | 111          | 2           |
| arberia                        | 7.9                   | 23    | 29.8          | 201743        | 829      | antedoro             | 4                 | 96           | 2           |
| hugo-theme-yue                 | 1.0                   | 34    | 29.8          | 5366          | 267      | CyrusYip             | 2                 | 226          | 0           |
| minimal_marketing              | 0.2                   | 21    | 29.6          | 25267         | 414      | letItCurl            | 2                 | 17           | 1           |
| hugo-theme-m10c                | 33.3                  | 485   | 29.4          | 7997          | 2206     | vaga                 | 21                | 67           | 9           |
| docura                         | 9.2                   | 70    | 29.2          | 6936          | 1014     | docura               | 5                 | 93           | 2           |
| Hugo-Octopress                 | 22.6                  | 158   | 29.1          | 18003         | 3290     | parsiya              | 13                | 140          | 8           |
| theme                          | 1.3                   | 14    | 28.8          | 10671         | 294      | hugo-porto           | 2                 | 158          | 1           |
| kidlat                         | 0.1                   | 2     | 28.7          | 1258          | 332      | kidlat2024           | 3                 | 12           | 0           |
| HugoTeX                        | 19.6                  | 114   | 28.7          | 14710         | 1709     | kaisugi              | 11                | 83           | 0           |
| kayal                          | 1.3                   | 18    | 28.5          | 15498         | 200      | mnjm                 | 3                 | 151          | 4           |
| am-writing-hugo-theme          | 1.9                   | 1     | 28.4          | 19927         | 430      | Wivik                | 2                 | 67           | 0           |
| magnolia-free-hugo-theme       | 1.3                   | 24    | 28.2          | 8597          | 179      | ololiuhqui           | 5                 | 91           | 0           |
| freshpink                      | 2.2                   | 10    | 28.2          | 5008          | 327      | elecbrandy           | 4                 | 95           | 0           |
| saral                          | 3.0                   | 9     | 28.2          | 1772          | 489      | dipeshsingh253       | 2                 | 87           | 4           |
| hugo-theme-nostyleplease       | 14.6                  | 281   | 28.1          | 11964         | 893      | hanwenguo            | 10                | 61           | 5           |
| hugo_theme_windy               | 0.9                   | 4     | 28.1          | 28092         | 235      | zEttOn86             | 1                 | 122          | 0           |
| hugo-pure                      | 3.6                   | 7     | 28.1          | 3892          | 494      | undus5               | 2                 | 127          | 0           |
| terminal-hugo-theme            | 1.4                   | 24    | 27.9          | 9207          | 308      | techbarrack          | 2                 | 50           | 1           |
| hugo-theme-pixyll              | 25.0                  | 182   | 27.3          | 11196         | 3734     | azmelanar            | 13                | 139          | 6           |
| hugo-PolyRhythmic              | 1.6                   | 23    | 27.3          | 58787         | 172      | wonyoung-jang        | 2                 | 68           | 1           |
| hugo-saasify-theme             | 0.7                   | 18    | 26.9          | 27860         | 79       | chaoming             | 2                 | 67           | 0           |
| black                          | 0.3                   | 1     | 26.9          | 1528          | 222      | SunkenPotato         | 1                 | 3            | 0           |
| hugo-theme-reimu               | 1.0                   | 34    | 26.9          | 16713         | 98       | D-Sketon             | 1                 | 94           | 0           |
| hugo-theme-til                 | 1.2                   | 80    | 26.8          | 21010         | 100      | michenriksen         | 1                 | 31           | 0           |
| zahi                           | 2.9                   | 18    | 26.6          | 4325          | 355      | mohamedelhefni       | 2                 | 26           | 0           |
| port-hugo                      | 21.2                  | 23    | 26.3          | 31634         | 1834     | tylersayshi          | 8                 | 87           | 1           |
| hugo-theme-quint               | 3.4                   | 39    | 26.2          | 20923         | 276      | victoriadrake        | 2                 | 40           | 0           |
| HikaeMe                        | 1.8                   | 2     | 26.2          | 12932         | 179      | htnabe               | 1                 | 76           | 2           |
| theme-long-teng                | 0.9                   | 5     | 26.0          | 17186         | 83       | mdfriday             | 2                 | 17           | 2           |
| simple-style                   | 19.8                  | 33    | 26.0          | 1244          | 1888     | yanlinlin82          | 4                 | 80           | 1           |
| Ardeidae                       | 5.7                   | 7     | 26.0          | 38935         | 548      | LuisSousaRego        | 1                 | 42           | 0           |
| hugo-theme-island              | 0.6                   | 0     | 25.9          | 14408         | 40       | bin16                | 1                 | 61           | 0           |
| hugo-theme-console             | 29.5                  | 500   | 25.7          | 19804         | 1740     | mrmierzejewski       | 9                 | 58           | 0           |
| hugo-brewm                     | 0.2                   | 5     | 25.7          | 12851         | 7        | foxihd               | 1                 | 29           | 0           |
| coming-soon                    | 7.2                   | 16    | 25.5          | 7722          | 520      | mansoorbarri         | 4                 | 68           | 1           |
| hugo-simple                    | 7.0                   | 53    | 25.5          | 3094          | 439      | maolonglong          | 4                 | 63           | 1           |
| hugo-whisper-theme             | 27.7                  | 266   | 25.4          | 17325         | 2179     | zerostaticthemes     | 12                | 64           | 6           |
| hugo-xmag                      | 24.6                  | 108   | 25.3          | 1398          | 2790     | yihui                | 10                | 109          | 6           |
| hugo-news                      | 0.9                   | 2     | 25.3          | 37830         | 23       | professionalaf       | 1                 | 10           | 0           |
| vinyl-records-collection-theme | 7.5                   | 7     | 25.2          | 3567          | 534      | Wivik                | 4                 | 64           | 1           |
| theme-search                   | 2.3                   | 2     | 25.0          | 7236          | 101      | hbstack              | 3                 | 9            | 1           |
| hugo-winston-theme             | 25.4                  | 275   | 24.7          | 5743          | 1597     | zerostaticthemes     | 10                | 47           | 2           |
| hugo-theme-fluidity            | 2.0                   | 0     | 24.6          | 7104          | 65       | wayjam               | 1                 | 32           | 0           |
| maverick                       | 15.3                  | 50    | 24.3          | 8537          | 954      | canhtran             | 9                 | 63           | 8           |
| pehtheme-hugo                  | 8.8                   | 59    | 24.1          | 11207         | 480      | fauzanmy             | 4                 | 28           | 3           |
| cyberscape                     | 11.3                  | 19    | 23.6          | 8197          | 813      | isaksolheim          | 2                 | 36           | 0           |
| roxo-hugo                      | 30.5                  | 207   | 23.4          | 25440         | 1793     | StaticMania          | 16                | 43           | 10          |
| smol                           | 35.6                  | 277   | 23.3          | 822           | 3034     | colorchestra         | 11                | 74           | 10          |
| hugo-story                     | 37.1                  | 217   | 23.3          | 214490        | 1678     | caressofsteel        | 12                | 41           | 7           |
| agnes-hugo-theme               | 10.3                  | 26    | 23.0          | 2848          | 538      | dchucks              | 5                 | 31           | 0           |
| simple-dark                    | 8.1                   | 2     | 22.9          | 14192         | 414      | MichaelSchaecher     | 2                 | 48           | 1           |
| hugo-dpsg                      | 24.2                  | 32    | 22.5          | 10339         | 1558     | pfadfinder-konstanz  | 12                | 64           | 2           |
| yuan                           | 9.1                   | 4     | 22.3          | 2059          | 508      | 17ms                 | 1                 | 35           | 0           |
| vncnt-hugo                     | 26.2                  | 67    | 22.2          | 15419         | 2224     | fncnt                | 7                 | 75           | 1           |
| almeida-cv                     | 30.6                  | 203   | 21.6          | 9562          | 1633     | ineesalmeida         | 15                | 53           | 2           |
| spectral                       | 27.6                  | 77    | 21.6          | 16750         | 2707     | sbruder              | 8                 | 82           | 4           |
| hugo-menu                      | 8.3                   | 0     | 21.4          | 1148          | 322      | gentleadam           | 1                 | 37           | 0           |
| bloggraph                      | 17.3                  | 3     | 21.4          | 50700         | 1102     | desmondlzy           | 2                 | 62           | 0           |
| compost                        | 18.8                  | 55    | 21.3          | 13305         | 1226     | canstand             | 1                 | 59           | 1           |
| whiteplain                     | 32.2                  | 136   | 21.2          | 2858          | 2602     | taikii               | 11                | 77           | 8           |
| hugo-black-and-light-theme     | 50.5                  | 193   | 21.2          | 5301          | 2947     | davidhampgonsalves   | 9                 | 51           | 4           |
| hugo-starter                   | 26.0                  | 22    | 21.2          | 13461         | 2203     | jimfrenette          | 5                 | 84           | 1           |
| hugo-theme-flat                | 17.5                  | 29    | 21.0          | 67175         | 1014     | leafee98             | 2                 | 57           | 0           |
| E25DX                          | 10.9                  | 74    | 20.8          | 3543          | 400      | dumindu              | 1                 | 17           | 0           |
| blank                          | 96.2                  | 232   | 20.6          | 1629          | 3034     | Vimux                | 6                 | 28           | 2           |
| hugo-cuisine-book              | 17.5                  | 11    | 20.6          | 26108         | 935      | ntk148v              | 5                 | 52           | 1           |
| hugo-travelify-theme           | 29.2                  | 39    | 19.9          | 59477         | 2778     | balaramadurai        | 7                 | 91           | 3           |
| hugo-dusk                      | 29.7                  | 57    | 19.8          | 5681          | 2845     | gyorb                | 9                 | 95           | 2           |
| hugo-cards                     | 33.1                  | 82    | 19.4          | 9866          | 2320     | bul-ikana            | 8                 | 67           | 1           |
| hugo-digital-garden-theme      | 23.6                  | 95    | 19.1          | 33351         | 1266     | paulmartins          | 4                 | 39           | 4           |
| heyo-hugo-theme                | 14.5                  | 23    | 19.0          | 33397         | 546      | LucasVadilho         | 2                 | 29           | 0           |
| hugo-changelog-theme           | 34.3                  | 107   | 18.8          | 1278          | 2349     | jsnjack              | 5                 | 69           | 3           |
| hugo-arcana                    | 24.8                  | 35    | 18.5          | 31487         | 1265     | half-duplex          | 8                 | 49           | 1           |
| paperesque                     | 29.3                  | 68    | 18.3          | 8418          | 1962     | capnfabs             | 3                 | 67           | 4           |
| glim-midnight                  | 13.6                  | 8     | 18.2          | 7232          | 452      | mansoorbarri         | 1                 | 32           | 0           |
| hugo-theme-terminalcv          | 23.3                  | 140   | 18.0          | 1271          | 989      | coolapso             | 6                 | 39           | 0           |
| hugo-now                       | 44.3                  | 23    | 18.0          | 61553         | 2773     | mikeblum             | 5                 | 52           | 0           |
| internet-weblog                | 55.9                  | 40    | 17.8          | 16990         | 3272     | jnjosh               | 5                 | 58           | 0           |
| hackropole-hugo                | 12.8                  | 11    | 17.6          | 41155         | 266      | ANSSI-FR             | 1                 | 21           | 3           |
| bootstrap-bp-hugo-startpage    | 50.3                  | 65    | 17.4          | 45491         | 2024     | spech66              | 2                 | 40           | 0           |
| silhouette-hugo                | 81.4                  | 26    | 17.2          | 6957          | 2241     | mattbutton           | 5                 | 22           | 3           |
| materialize-bp-hugo-theme      | 39.6                  | 19    | 17.0          | 33348         | 1962     | spech66              | 3                 | 49           | 0           |
| BlogRa                         | 34.0                  | 17    | 16.9          | 322405        | 1508     | rafed                | 2                 | 42           | 0           |
| fruhling                       | 15.6                  | 3     | 16.8          | 79151         | 381      | romka                | 2                 | 21           | 1           |
| hugo-rocinante                 | 80.2                  | 52    | 16.6          | 22980         | 1797     | mavidser             | 2                 | 22           | 4           |
| hugo-spectre-pixel-theme       | 181.3                 | 16    | 16.6          | 4079          | 1971     | st-wong              | 4                 | 11           | 2           |
| sada                           | 44.7                  | 24    | 16.5          | 8203          | 2241     | darshanbaral         | 2                 | 43           | 1           |
| hugo_theme_adam_eve            | 35.6                  | 17    | 16.4          | 5200          | 2784     | blankoworld          | 1                 | 79           | 0           |
| kitab                          | 36.4                  | 21    | 16.2          | 3631          | 2088     | darshanbaral         | 1                 | 55           | 2           |
| hugo-theme-doors               | 62.9                  | 18    | 16.2          | 8516          | 2010     | zzzmisa              | 2                 | 26           | 0           |
| hugo-theme-fluency             | 32.6                  | 55    | 15.9          | 8491          | 1729     | wayjam               | 1                 | 51           | 0           |
| galleriesdeluxe                | 19.4                  | 45    | 15.9          | 48298         | 582      | bep                  | 3                 | 25           | 0           |
| hugo-theme-hulga               | 34.5                  | 32    | 15.5          | 34387         | 1544     | wlh320               | 5                 | 44           | 3           |
| gallerydeluxe                  | 25.1                  | 158   | 14.9          | 3823          | 870      | bep                  | 3                 | 31           | 9           |
| simple-resume                  | 54.0                  | 30    | 14.7          | 2458          | 1580     | tylersayshi          | 3                 | 30           | 0           |
| simple-snipcart-shop           | 181.6                 | 8     | 14.1          | 94024         | 1465     | tylersayshi          | 3                 | 9            | 0           |
| build-your-website             | 15.5                  | 2     | 14.1          | 3566          | 158      | jingplay             | 2                 | 5            | 0           |
| flex-bp-hugo-cv                | 57.2                  | 9     | 13.7          | 26206         | 1550     | spech66              | 1                 | 27           | 0           |
| calligraphy                    | 183.2                 | 31    | 10.6          | 115089        | 1047     | pacollins            | 1                 | 6            | 0           |
| huey                           | 44.4                  | 12    | 10.4          | 38100         | 1132     | alloydwhitlock       | 1                 | 25           | 0           |
| re-cover                       | 61.1                  | 1     | 10.2          | 2114          | 1188     | sieis                | 1                 | 12           | 0           |
| quietfoodie                    | 58.6                  | 2     | 10.1          | 46941         | 1079     | paposeco             | 2                 | 15           | 0           |
| hugo-theme-huguette            | 33.0                  | 4     | 9.5           | 19786         | 1025     | cathelijne           | 2                 | 17           | 1           |
| TatBanTheme2.0                 | 37.3                  | 1     | 9.2           | 4757          | 1018     | tatsatb              | 2                 | 17           | 1           |
