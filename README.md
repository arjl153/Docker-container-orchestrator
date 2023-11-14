# Docker-container-orchestrator

This project, developed as part of a Cloud Computing course in January 2019, is a cloud-based Web Application designed for photo sharing.
Utilizing the Django framework, the application is built around a REST API, providing a scalable and efficient platform for users to share their photos.

<h2>Features</h2>
<ul>
  <li><h3>Microservices Architecture:</h3><span>The application is structured into two microservices for improved modularity and scalability.</span></li>
  <li><h3>Dockerized Deployment:</h3><span>Leveraging Docker containers, the application is encapsulated for easy deployment, ensuring consistency across different environments.</span></li>
  <li><h3>AWS Infrastructure:</h3><span>The Docker containers are hosted on separate AWS EC2 instances, taking advantage of the scalability and reliability offered by Amazon Web Services.</span></li>
  <li><h3>Container Orchestration:</h3><span>A custom-built container orchestrator is implemented to handle auto-scaling and load balancing. The orchestrator dynamically adjusts the number of server containers based on the volume and type of incoming requests.</span></li>
  <li><h3>Auto-Scaling:</h3><span>In response to high workloads, the container orchestrator automatically increases the count of servers to distribute the load efficiently.</span></li>
  <li><h3>Load Balancing:</h3><span>The container orchestrator employs load balancing techniques to optimize resource utilization, ensuring a smooth and responsive experience for users.</span></li>
</ul>
