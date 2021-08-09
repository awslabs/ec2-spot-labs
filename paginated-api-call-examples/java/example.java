/** 
# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

/**
#####################
Example Java function for making a paginated Describe call.
#####################
*/

import com.amazonaws.services.ec2.model.DescribeSpotInstanceRequestsRequest;
import com.amazonaws.services.ec2.model.DescribeSpotInstanceRequestsResult;
import com.amazonaws.services.ec2.model.SpotInstanceRequest;

    private DescribeSpotInstanceRequestsResult makePaginatedDescribe() {
         final DescribeSpotInstanceRequestsRequest describeRequest = new DescribeSpotInstanceRequestsRequest().withMaxResults(20);
         final List<SpotInstanceRequest> spotRequests = new ArrayList<>();
         String nextToken = null;
         do {
             if (nextToken != null) {
                 describeRequest.setNextToken(nextToken);
             }
             DescribeSpotInstanceRequestsResult result = amazonEC2Client.describeSpotInstanceRequests(describeRequest);
             spotRequests.addAll(result.getSpotInstanceRequests());
             nextToken = result.getNextToken();
         } while (nextToken != null);
         log.info("Initial describe result:" + spotRequests.size());
         return new DescribeSpotInstanceRequestsResult().withSpotInstanceRequests(spotRequests);
     }