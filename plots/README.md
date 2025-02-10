# plots

```bash
git log --date=short --pretty=format:'%ad' | sort | uniq -c
```

```bash
## Use sample data
python main.py

## Use custom input file
python main.py -i commit_data.txt

## Save plot to file instead of displaying
python main.py -i commit_data.txt -o plot.png

## Use sample data but save to file
python main.py -o plot.png
```
