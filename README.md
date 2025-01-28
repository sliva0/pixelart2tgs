# pixelart2tgs

Simple .gif to .tgs converter cli utility.

![Source GIF](https://github.com/sliva0/pixelart2tgs/raw/master/images/ralsei.gif)
![Tg demonstation](https://github.com/sliva0/pixelart2tgs/raw/master/images/tg.gif)


## Warning

This project was developed before [Telegram update][UPD] added WebM format for stickers and emojis.

Before using this project, consider using WebM instead - it can handle higher resolution and framerate,
and I also wrote a utility for working with it: [tgradish][TGR].

You might still want to use this project if you want to make scalable animated pixel art emojis -  see [example][RGI].

[UPD]: https://telegram.org/blog/video-stickers-better-reactions
[TGR]: https://github.com/sliva0/tgradish
[RGI]: https://github.com/sliva0/pixelart2tgs/issues/7


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
second.gif -> sticker.tgs
```

## License

[MIT License](LICENSE.txt)
