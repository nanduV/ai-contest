// Copyright 2010 owners of the AI Challenge project
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy
// of the License at http://www.apache.org/licenses/LICENSE-2.0 . Unless
// required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Author: Jeff Cameron (jeff@jpcameron.com)
//
// Stores a Tron map and keeps it up to date throughout a game of Tron. A Tron
// map is a rectangular array of cells. Each cell is either passable or
// non-passable.

#ifndef TRON_ENGINE_MAP_H_
#define TRON_ENGINE_MAP_H_

#include <cstdio>
#include <vector>

class Map {
 public:
  // Constructs a map by reading it out of a text file.
  Map(const std::string& filename);

  // Writes the board to a file handle. If file_pointer is not specified, the
  // default behavior is to write to stdout.
  void Write(FILE *file_pointer = stdout, bool swap = false) const;

  // The size of the map.
  int Width() const;
  int Height() const;
  const Point& Dimensions() const;

  // The locations of the two players
  const Point& PlayerOneLocation() const;
  const Point& PlayerTwoLocation() const;

  // If the given square is a wall, returns true. If the given square is
  // passable, returns false. If the square is outside the map, returns true.
  bool IsWall(int x, int y);
  bool IsWall(const Point& p);

  // 

 private:
  // Returns whether or not the given coordinates are valid on this map.
  bool OnMap(int x, int y);
  bool OnMap(const Point& p);

  std::vector<std::vector<bool> > cells_;
  Point dimensions_;
  Point player_one_location_;
  Point player_two_location_;
}

#endif
