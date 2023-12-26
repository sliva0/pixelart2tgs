# pixelart2tgs

Simple .gif to .tgs converter cli utility.

![Source GIF]![Screenshot_2023_1219_003346](https://github.com/Deyvey/codespaces-blank/assets/88993196/a6aec8aa-95e2-4a64-a1fe-2dc4ff97c723)
![Tg demonstation](https://github.com/liebert/pixelart2tgs/raw/master/images/tg.gif)


## Warning

After [update of Telegram with the addition of video stickers][UPD], this project lost all practical meaning. If you need to make animated stickers from GIFs after January 2022, use [tgradish][TGR].

[UPD]: https://telegram.org/blog/video-stickers-better-reactions
[TGR]: https://github.com/sliva0/tgradish

## Some not so user friendly alternatives

 - [MattBas's lottie](https://pypi.org/project/lottie/)
 - [bodqhrohro's giftolottie](https://github.com/bodqhrohro/giftolottie)


## Installation

``` console
python -m pip install pixelart2tgs
```

and then usage:

``` console
python -m pixelart2tgs
```


## Usage examples

``` console
$ pixelart2tgs -i input.gif
input.gif -> input.tgs
```

``` console
$ pixelart2tgs -i first.gif -i second.gif sticker.tgs -y
first.gif -> first.tgs
second.gif -> "sticker.tgs
```

## License

[MIT License](LICENSE.txt)
