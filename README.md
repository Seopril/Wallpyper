# Wallpyper

Wallpyper is a simply python application to automatically update your desktop background.

It pulls from a configured list of a subreddits for new images based on variable Reddit sorting.

Before running this application, the WALLPYPER_CLIENT_ID and WALLPYPER_CLIENT_SECRET
environment variables must be set. To do this, create new Reddit bot credentials and use these.

## Config Settings

The configuration file will look something like this:

```
[DEFAULT]
image_path
resolution
aspect_ratio
limit_resolution
limit_aspect_ratio
allow_larger_resolution
allow_nsfw
sort_by
sort_limit
history
```

`image_path` points to the desired directory to save the images.

`resolution` specifies the target resolution of the wallpaper.

`aspect_ratio` specifies the target aspect ratio of the wallpaper.

`limit_resolution` is a boolean which specifies if the resolution should be limited.

`limit_aspect_ratio` is a boolean which specifies if the aspect ratio should be limited.

`allow_larger_resolution` is the maximum resolution if `limit_resolution` is set to true.

`allow_nfsw` is a boolean which allows for posts marked as "NSFW" on Reddit to be included in the image set.

`sort_by` is the Reddit sorting method.

`sort_limit` is the number of posts returned from the Reddit sort.

`history` is a boolean which specifies if past wallpapers should be reused if it matches the search criteria.