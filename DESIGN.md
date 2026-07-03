# DZRP Item Catalog Design

## Mission

Help DayZRP staff find, understand, and use server items quickly.

## Core Principles

1. Find the correct item in under 10 seconds.
2. Never require deep DayZ item knowledge.
3. Everything is connected.
4. Never lose your place.
5. Keep official data, DZRP server data, and staff knowledge separate.
6. The catalog should get smarter as staff use it.

## Data Layers

### Official Data
Imported from DayZ/mod configs.

- Display name
- Classname
- Category
- Image
- Description
- Compatibility

### DZRP Server Data
Specific to how DZRP uses the item.

- Enabled
- Disabled
- Item shop
- Trader
- Event only
- Admin only
- Faction only

### Staff Knowledge
Editable by staff.

- Tags
- Notes
- Common player descriptions
- Aliases

## Required Navigation

Every item page needs:

- Back to Search Results
- Back to Previous Item
- Clickable related items

## Version 0.1 Goals

- Homepage
- Search bar
- Item cards
- Item detail page
- Item image
- Display name
- Classname
- Copy classname button
- Server status badge
- Staff tags display