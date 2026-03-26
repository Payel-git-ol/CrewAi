package fetcher

import (
	"crewai/internal/core/services/create"
	"crewai/pkg/requests"
	"github.com/Payel-git-ol/azure"
)

func HttpManager(a *azure.Azure) {
	a.Use(azure.Recovery())
	a.Use(azure.Logger())

	a.Get("/health", func(c *azure.Context) {
		c.JsonStatus(200, azure.M{
			"status": "OK",
		})
		return
	})

	a.Post("/new/task", func(c *azure.Context) {
		var reqTask requests.TaskRequest

		if err := c.BindJSON(&reqTask); err != nil {
			c.JsonStatus(azure.StatusUnauthorized, azure.M{
				"status": "fatal",
				"error":  err.Error(),
			})
			return
		}

		response, err := create.CreateGrpcResponse(reqTask)
		if err != nil {
			c.JsonStatus(azure.StatusBadRequest, azure.M{
				"status": "fatal",
				"error":  err.Error(),
			})
			return
		}

		c.JsonStatus(azure.StatusOK, azure.M{
			"status":   response.Status,
			"data":     response.Solution,
			"taskName": response.Taskname,
		})
		return
	})
}
