# pixelart2tgs

Simple .gif to .tgs converter cli utility.

![Source GIF](https://github.com/sliva0/pixelart2tgs/raw/master/images/ralsei.gif)
![Tg demonstation](https://github.com/sliva0/pixelart2tgs/raw/master/images/tg.gif)


## Warning

After [update of Telegram with the addition of video stickers][UPD], this project lost all practical meaning. If you need to make animated stickers from GIFs after January 2022, use `ffmpeg`.

[UPD]: https://telegram.org/blog/video-stickers-better-reactions


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
