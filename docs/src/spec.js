export const spec = {
  "swagger": "2.0",
  "info": {
    "description": "Retrieve .btc Leaderboard data using this paginated API.",
    "version": "1.0.0",
    "title": ".btc Leaderboard API"
  },
  "host": "btcleaderboard.xyz",
  "schemes": [
    "https"
  ],
  "tags": [
    {
      "name": "Leaderboard"
    }
  ],
  "paths": {
    "/api": {
      "get": {
        "tags": [
          "Leaderboard"
        ],
        "operationId": "leaderboard",
        "produces": [
          "application/json"
        ],
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "description": "Specify the number of results to be returned (max. 200)",
            "required": true,
            "type": "integer"
          },
          {
            "name": "offset",
            "in": "query",
            "description": "Specify the number of results to be skipped",
            "required": true,
            "type": "integer"
          }
        ],
        "responses": {
          "200": {
            "description": "successful operation",
            "schema": {
              "type": "array",
              "items": {
                "$ref": "#/definitions/APIResponse"
              }
            }
          },
          "400": {
            "description": "Max limit can be 200"
          }
        }
      }
    }
  },
  "definitions": {
    "APIResponse": {
      "type": "object",
      "properties": {
        "twitter_id": {
          "type": "string",
          "example": "3285797414"
        },
        "twitter_name": {
          "type": "string",
          "example": "stacks.btc"
        },
        "twitter_username": {
          "type": "string",
          "example": "Stacks"
        },
        "twitter_follower_count": {
          "type": "integer",
          "example": 133727
        }
      }
    }
  }
};
