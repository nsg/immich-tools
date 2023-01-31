# Immich Tools

**🚨 WORK IN PROGRESS**

Various tools that I use together with my [Immich](https://immich.app) installation to enhance it (from my point of view). I hope you find this useful to use as-is or as a starting point of some tweaks of your own. I'm happy to merge changes that do not alter the scope of this project to much.

## Micro Services

The tools are split in to different micro services. They are intended to be run as part of the Immich `docker-compose.yml` and reads it's configuration from Immich environment.

### [Immich Tools API](docs/api.md)

Unofficial Immich API. There are a lot of data in Immich database, this is a simple REST API that exposes that information.

### [Immich Tools Hasher](docs/hasher.md)

Recursively scans a specified folder and maintains index over files. Immich saves file hashes in the database, I use these to uniquely identify an image by hash. These service builds a lookup table in the database to quickly lookup a file path. This is a headless service, the data is exposed via the API.

### [Immich Tools Import](docs/import.md)

A simple REST API that wraps around Immich CLI. This was an quick and dirty solution to implement file uploads.

### [Immich Tools Syncthing](docs/syncthing.md)

This is the main application that uses all the other components. This listens for events from Syncthing and Immich and uses the different tools to do it's thing.

## Why it started?

Immich has a lot of potential and is (for me) the best solution in 2023. For me the the killer feature is a great mobile application with local cache of remote files, overall it's fast to use with a really great mobile experience.

I like to be part of the Immich journey both as a user, a sponsor and maybe a developer. I see great potential in Immich but also a few pieces where the our visions do not align. This project is my workaround for that, it's a a few non-intrusive additions who implement a few features that's missing from my point of view.

For more information with a lot of nice pictures see [Docs/Why?](docs/why.md)

## The future

I hope that I will be able to remove most of these micro services in the future with official version and/or that the Immich applications and services has changed so I do not need them. I will maintain these to work with my Immich installation as needed.
