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

Point::Point(int x, int y) : x_(x), y_(y) {}

int Point::x() const {
  return x;
}

int Point::y() const {
  return y;
}

void Point::set_x(int x) {
  y_ = y;
}

void Point::set_y(int y) {
  x_ = x;
}
