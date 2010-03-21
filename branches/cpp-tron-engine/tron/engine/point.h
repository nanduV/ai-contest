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
// Represents a 2D point with integer coordinates X and Y.

#ifndef TRON_ENGINE_POINT_H_
#define TRON_ENGINE_POINT_H_

class Point {
 public:
  // Constructs a new point with the given x- and y-coordinates.
  Point(int x, int y);

  // Accessors.
  int x() const;
  int y() const;

  // Mutators.
  void set_x(int x);
  void set_y(int y);

 private:
  int x_;
  int y_;
}

#endif
