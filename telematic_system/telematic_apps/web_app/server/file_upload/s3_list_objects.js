/*
 * Copyright (C) 2019-2024 LEIDOS.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 * 
 * Description:
 * Get a list of S3 object from pre-configured S3 bucket using NODE.js S3 client.
 * 
 * - listObjects: Return a list of objects from pre-configured S3 bucket.
 */

const { ListObjectsV2Command, S3Client } = require("@aws-sdk/client-s3");
require("dotenv").config();

const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
const secretAccessKey = process.env.AWS_SECRET_KEY;
const region = process.env.S3_REGION;
const bucket = process.env.S3_BUCKET;

exports.listObjects = async () => {
  const client = new S3Client({
    credentials: {
      accessKeyId,
      secretAccessKey,
    },
    region,
  });
  const command = new ListObjectsV2Command({
    Bucket: bucket,
  });
  let contents = [];
  let isTruncated = true;
  while (isTruncated) {
    const { Contents, IsTruncated, NextContinuationToken } = await client.send(
      command
    );
    const contentsList = Contents.map((c) => ({
      original_filename: c.Key,
      size: c.Size,
      filepath: bucket,
    }));
    isTruncated = IsTruncated;
    contents.push(...contentsList);
    command.input.ContinuationToken = NextContinuationToken;
  }
  return contents;
};
