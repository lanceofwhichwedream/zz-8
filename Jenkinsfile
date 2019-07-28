#!groovy

node {

  def err = null
  currentBuild.result = "SUCCESS"

  try {
    stage 'Checkout'
      checkout scm
			sh "docker kill zz8"
			sh "docker rm zz8"

    stage 'Validate'
      def packer_file = 'zz8.json'
      print "Running packer validate on : ${packer_file}"
      sh "packer -v ; packer validate ${packer_file}"

    stage 'Build'
      sh "packer build ${packer_file}"

		stage 'Deploy'
			sh "docker run --name zz8 --detach -it lanceofwhichwedream/home-network:zz8"
  }

  catch (caughtError) {
    err = caughtError
    currentBuild.result = "FAILURE"
  }

  finally {
    /* Must re-throw exception to propagate error */
    if (err) {
      throw err
    }
  }
}
