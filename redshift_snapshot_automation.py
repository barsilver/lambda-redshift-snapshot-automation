import boto3
import botocore
import os
import json

def describe_cluster(cluster_id):
    redshift_client = boto3.client('redshift')
    response = redshift_client.describe_clusters(ClusterIdentifier=cluster_id)

    # Assuming only one cluster is returned; you might handle multiple results differently
    cluster_description = response['Clusters'][0]

    return cluster_description

def lambda_handler(event, context):
    # Initialize Redshift client
    redshift_client = boto3.client('redshift')

    # Access the CloudWatch event details
    event_details = event['detail']

    # Log the event details
    print("Received event: " + json.dumps(event))

    # Extract relevant information about the snapshot
    source_cluster_id = event_details['sourceIdentifier']
    target_cluster_id = source_cluster_id + "-archive"

    # Retrieve the source cluster's configuration details
    source_cluster_details = describe_cluster(source_cluster_id)
    
    # Use the source cluster's configuration to create the target cluster
    try:
        response = redshift_client.create_cluster(
            ClusterIdentifier=target_cluster_id,
            NodeType=source_cluster_details['NodeType'],
            ClusterType=source_cluster_details['ClusterType'],
            # Add more parameters here as needed
        )
        print(f"Creating Redshift cluster: {target_cluster_id}")
        
        # Wait for the cluster to become available
        redshift_client.get_waiter('cluster_available').wait(ClusterIdentifier=target_cluster_id)
        print(f"Redshift cluster {target_cluster_id} is available")
        
        # Take a snapshot of the new cluster
        snapshot_id = f"{target_cluster_id}-snapshot"
        redshift_client.create_cluster_snapshot(
            SnapshotIdentifier=snapshot_id,
            ClusterIdentifier=target_cluster_id,
        )
        print(f"Creating snapshot {snapshot_id} from Redshift cluster {target_cluster_id}")
        
        # Wait for the snapshot to complete
        redshift_client.get_waiter('snapshot_completed').wait(SnapshotIdentifier=snapshot_id)
        print(f"Snapshot {snapshot_id} is completed")
        
        # Delete the new Redshift cluster
        redshift_client.delete_cluster(
            ClusterIdentifier=target_cluster_id,
            SkipFinalClusterSnapshot=True  # Avoid creating a final snapshot
        )
        print(f"Deleting Redshift cluster {target_cluster_id}")
        
    except botocore.exceptions.ClientError as e:
        print(f"Error: {str(e)}")
        raise
    
    # Return a response indicating success
    return {
        'statusCode': 200,
        'body': 'Snapshot creation and cluster deletion completed successfully'
    }

