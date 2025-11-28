#! /bin/bash
# This script renames all essentials components of the project. This can be useful at deployment time.

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# check that the folder contains a docker-compose.production.yml file
if [ ! -f docker-compose.production.yml ]; then
    echo -e "${RED}Error: docker-compose.production.yml not found!${RESET}"
    echo -e "${YELLOW}Make sure you are in the root directory of the project.${RESET}"
    exit 1
fi

# get the new name from the command line argument as $1
NEW_NAME="$1"

# If the new name is empty prompt the user to enter a name
while [ -z "$NEW_NAME" ]; do
    echo -e "${CYAN}Let's give your project a shiny new name!${RESET}"
    read -e -p "Enter the new project name (Ctrl + C to cancel): " NEW_NAME
    READ_STATUS=$?
    if [ -z "$NEW_NAME" ]; then
        echo -e "${YELLOW}Don't be shy, your project deserves a name!${RESET}"
        continue
    fi
done

# Slugify function: lowercase, replace spaces with _, remove non-alphanum/underscore/hyphen
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]+/_/g' | sed -E 's/^_+|_+$//g'
}

SLUGIFIED_NAME=$(slugify "$NEW_NAME")

if [ "$NEW_NAME" != "$SLUGIFIED_NAME" ]; then
    echo -e "${YELLOW}The project name should be slugified.${RESET}"
    echo -e "${CYAN}Suggested name: ${BOLD}$SLUGIFIED_NAME${RESET}"
    read -e -p "Use suggested name? [Y/n]: " USE_SUGGESTED
    if [[ "$USE_SUGGESTED" =~ ^[Yy]([Ee][Ss])?$ || -z "$USE_SUGGESTED" ]]; then
        NEW_NAME="$SLUGIFIED_NAME"
        echo -e "${GREEN}Great choice!${RESET}"
    else
        # Prompt again for a valid slugified name
        while true; do
            read -e -p "Enter a slugified project name: " NEW_NAME
            SLUGIFIED_NAME=$(slugify "$NEW_NAME")
            if [ "$NEW_NAME" = "$SLUGIFIED_NAME" ] && [ -n "$NEW_NAME" ]; then
                echo -e "${GREEN}Looks perfect!${RESET}"
                break
            else
                echo -e "${RED}Name must be slugified (lowercase, alphanumeric, _, -).${RESET}"
            fi
        done
    fi
fi

# Get the current project name from the docker-compose file:
CURRENT_NAME=$(grep -oP 'image:\s*\K([a-zA-Z0-9_-]+)(?=_production_django)' docker-compose.production.yml)

# print the current and new name
echo -e "${CYAN}Current project name: ${BOLD}$CURRENT_NAME${RESET}"
echo -e "${CYAN}New project name: ${BOLD}$NEW_NAME${RESET}"

# Confirm with the user
echo -e "${YELLOW}Are you sure you want to rename the project from '${BOLD}$CURRENT_NAME${RESET}${YELLOW}' to '${BOLD}$NEW_NAME${RESET}${YELLOW}'?${RESET}"
read -e -p "[y/N]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]([Ee][Ss])?$ || -z "$CONFIRM" ]]; then
    echo -e "${RED}Renaming cancelled. Maybe next time!${RESET}"
    exit 0
fi

# rename docker-compose.production.yml
sed -i "s/${CURRENT_NAME}/${NEW_NAME}/g" docker-compose.production.yml
# rename docker-compose.local.yml
sed -i "s/${CURRENT_NAME}/${NEW_NAME}/g" docker-compose.local.yml
# rename .devcontainer/devcontainer.json
sed -i "s/${CURRENT_NAME}/${NEW_NAME}/g" .devcontainer/devcontainer.json

# exit with success message
echo -e "${GREEN}${BOLD}🎉 Project renamed successfully to '$NEW_NAME'! 🎉${RESET}"
echo -e "${CYAN}Please review the changes.${RESET}"
# Suggest to rebuild the docker images
echo -e "${YELLOW}You may want to rebuild the Docker images with:${RESET} ${BOLD}docker-compose -f docker-compose.local.yml build --no-cache${RESET} or the VSCode Dev Container."

exit 0
