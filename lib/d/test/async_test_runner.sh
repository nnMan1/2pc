#!/bin/bash

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

CUR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Runs the async test in both SSL and non-SSL mode.
${CUR}/async_test > /dev/null || exit 1
echo "Non-SSL tests done."

# THRIFT-4905: disabled the following test as it deadlocks / hangs
# ${CUR}/async_test --ssl > /dev/null || exit 1
# echo "SSL tests done."
echo "THRIFT-4905: SSL tests are disabled.  Fix them."
